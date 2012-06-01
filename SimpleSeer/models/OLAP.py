import logging
import calendar
from time import gmtime, localtime, mktime
from datetime import datetime

import mongoengine
import numpy as np
from formencode import validators as fev
from formencode import schema as fes
import formencode as fe

from ..realtime import ChannelManager
from SimpleSeer.util import utf8convert

from SimpleSeer import validators as V
from .base import SimpleDoc
from .Inspection import Inspection
from .Result import Result
from .Measurement import Measurement

log = logging.getLogger(__name__)


#################################
# name: Name of the OLAP object
# queryInfo: configuration used to construct ResultSet
# descInfo: configuration for the Descriptive statistic processing
# chartInfo: configuration for the chart to be displayed
# transInfo: configuration for final data transforms (normalize, etc)
#################################

class OLAPSchema(fes.Schema):
    name = fev.UnicodeString(not_empty=True)            
    queryInfo = V.JSON(not_empty=True)                  
    descInfo = V.JSON(if_empty=None, if_missing=None)   
    chartInfo = V.JSON(not_empty=True)
    transInfo = V.JSON(if_empty=None, if_missing=None)
    
    
#################################
# queryType: defines the type of objects to be queries (inspections, measurements, results
# TODO: queryType not implemented
# name: name of the object to lookup (object type defined by queryType)
# since: show only results with timestamp strictly greater than this time
# limit: limit the results returned to this number (by default, these are ordered by capture time)
# allow: number of records after which triggering automatic aggregation: THIS WILL CHANGE SOON
# aggregate: the descriptive statistic to use for the automatic aggregation: THIS WILL CHANGE SOON 
#################################
  
class QueryInfoSchema(fes.Schema):
    queryType = fev.OneOf(['inspection', 'measurement'], if_missing='inspection')
    name = fev.UnicodeString(not_empty = True)
    since = V.DateTime(if_empty=0, if_missing=None)
    limit = fev.Int(if_missing=None)
    allow = fev.Int(if_missing=None)
    aggregate = fev.OneOf(['moving', 'mean', 'median', 'mode', 'var', 'std', 'max', 'min', 'first', 'last', 'uq', 'lq'], if_missing=None)


#################################
# formula: the descriptive statistic to apply
# window: the time interval for grouping for the statistic, expressed in epoch seconds
# EXCEPTION: window for moving average currently does number of records, not time interval
# partial: how to handle results from incomplete time intervals (e.g., new data 30 seconds into a one minute interval)
# TODO: partial not yet implemented.  Currently just drops partial
#################################

class DescInfoSchema(fes.Schema):
    formula = fev.OneOf(['moving', 'mean', 'median', 'mode', 'var', 'std', 'max', 'min', 'first', 'last', 'uq', 'lq'], if_missing=None)
    window = fev.Int(if_missing=60)
    partial = fev.OneOf(['drop', 'raw', 'predict'], if_missing='drop')
    
    
#################################
# norm: Normalize the resulting input to [0, 1], boolean vaue
# devFromMedian: report results as number of standard deviations from median value, boolean value
# devFromBase: report results as number of standard deviations frmo a specified value, boolean value
# base: the base value used with devFromBase, number
#################################

class TransformSchema(fes.Schema):
    norm = fev.Int(if_missing=0)
    devFromMedian = fev.Int(if_missing=0)
    devFromBase = fev.Int(if_missing=0)
    base = fev.Int(if_missing=0)


#################################
# chartType: the style of chart to draw (e.g., bar, pie, etc)
# chartColor: the color of the lines in the chart
# TODO, color should maybe be validated to a hex string or web color
#################################

class ChartInfoSchema(fes.Schema):
    chartType = fev.OneOf(['line', 'bar', 'pie', 'spline', 'area', 'areaspline','column','scatter'])
    chartColor = fev.UnicodeString(if_empty="")

        

class OLAP(SimpleDoc, mongoengine.Document):
    # Basic OLAP setup:
    # - One Query to retrieve data from database
    # - One DescriptiveStatistic, computed from Queries
    # - Check if data set too large.  If so, move to different OLAP with aggregation
    # - Transform/normalize the data if necessary
    # - One Chart constructed from data provided
    
    
    # TODO: Have some inconsistent use of globals to clean up in here

    name = mongoengine.StringField()
    queryInfo = mongoengine.DictField()
    descInfo = mongoengine.DictField()
    chartInfo = mongoengine.DictField()
    transInfo = mongoengine.DictField()
    allow = mongoengine.IntField()
    aggregate = mongoengine.StringField()
    
    def __repr__(self):
        return "<OLAP %s>" % self.name
        
    def execute(self, sincetime = None, beforetime = None, limitresults = None):
        
        # Get the resultset
        queryinfo = self.queryInfo.copy()
        queryinfo = self.checkConfig(queryinfo, sincetime, beforetime, limitresults)
        
        r = ResultSet()
        resultSet = r.execute(queryinfo)
        
        # Check if any descriptive processing (and any data to process)
        if (self.descInfo) and (len(resultSet['data']) > 0):
            d = DescriptiveStatistic()
            resultSet = d.execute(resultSet, self.descInfo)
        
        
        # Also an implicit descriptive if too many results per chart
        # If exceeded, aggregate
        # Hard code in a default allow for backward compatibility
        if not self.allow: self.allow = 900
        if (len(resultSet['data']) > self.allow):
            of = OLAPFactory()
            self = of.fromBigOLAP(self, resultSet)
            
            # Redo the descriptive with the new aggregation
            d = DescriptiveStatistic()
            resultSet = d.execute(resultSet, self.descInfo)
            
        #TODO: Re-integrate transformations here
        
        # Create and return the chart
        c = Chart()
        chartSpec = c.createChart(resultSet, self.chartInfo, self.name)
        return chartSpec
        
        
    def checkConfig(self, queryInfo, sincetime, beforetime, limitresults):
        queryInfo['since'] = self.calcSince(queryInfo, sincetime)
        queryInfo['before'] = self.calcBefore(queryInfo, beforetime)
        queryInfo['limit'] = self.calcLimit(queryInfo, limitresults)
        if not queryInfo.has_key('allow'): queryInfo['allow'] = queryInfo['limit']
        if not queryInfo.has_key('aggregate'): queryInfo['aggregate'] = 'median'
        if not queryInfo.has_key('queryType'): queryInfo['queryType'] = 'inspection'
        
        return queryInfo
        
    def calcLimit(self, queryInfo, limit):
        # If provided a limit, always use that limit
        # Else, if defined in OLAP, use that limit
        # Otherwise, use a default of None
        if limit:
			return limit
        elif queryInfo.has_key('limit'):
            return queryInfo['limit']
        else:
			return None
        
        
    def calcSince(self, queryInfo, since):
        # If provided a time, always use that time
        # Else, if defined in OLAP, use that since time
        # Otherwise, use None
        if since:
			return since
        elif queryInfo.has_key('since'):
            return queryInfo['since'] 
        else:
            return None


    def calcBefore(self, queryInfo, before):
        # If provided a time, always use that time
        # Else, if defined in OLAP, use that since time
        # Otherwise, use None
        if before:
			return before
        elif queryInfo.has_key('before'):
            return queryInfo['before'] 
        else:
            return None

        
        
class OLAPFactory:
    # TODO: Not all config parameters set here yet
    # TODO: Make this more predictive.  Right now I'm just going to hard code a bunch of results
    
    def fromObject(self, obj):
        # Create an OLAP object from another query-able object
        # TODO: Need to add some more intelligence to this:
        
        queryinfo = dict()
        queryinfo['queryType'] = type(obj).lower()
        
        return self.makeOLAP(queryInfo = queryinfo)
        
    def fromBigOLAP(self, olap, resultSet):
        # Given a large OLAP object (returning too many records), return one with a descriptive transform to aggregate data
        # Assumes existing resultset provided, use that for computing size of object
        
        # TODO: this will clobber the aggregation function for moving average
        
        o = olap
        
        if (len(resultSet['data']) > o.allow):
            # Find an new appropriate level for aggregation
            interval = self.calcInterval(resultSet['data'], o.allow)
            
            # Define the aggregation function
            if (o.aggregate):
                agg = o.aggregate
            elif (o.descInfo.has_key('formula')):
                # If we are already using a descriptive, preserve it
                agg = o.descInfo['formula']
            else:
                agg = 'median'
            
            o.descInfo['formula'] = agg
            o.descInfo['window'] = interval
                
            # Make sure the rest of the setup is properly initialized
            o = self.makeOLAP(o.queryInfo, o.descInfo, o.transInfo, o.chartInfo)
        
            similar = OLAP.objects.filter(name=o.name)
            if (len(similar) == 0):
                log.info('made a new olap for aggregation: ' + o.name)
                o.save()
            else:
                log.info('switching to olap: ' + o.name)
                o = similar[0]
            
        return o
    
    def makeOLAP(self, queryInfo = dict(), descInfo = dict(), transInfo = dict(), chartInfo = dict()):
    
        # Makes a generic OLAP with default values
        # If any values are provided as parameters, keeps those and fills in the rest
    
        o = OLAP()
        o.queryInfo = self.makeQuery(queryInfo)
        o.descInfo = self.makeDesc(descInfo)
        o.transInfo = self.makeTrans(transInfo)
        o.chartInfo = self.makeChart(chartInfo)
        
        o.name = o.queryInfo['queryType'] + o.descInfo['formula'] + str(o.descInfo['window'])
        if not o.allow: o.allow = 900
        if not o.aggregate: o.aggregate = 'median'
        
        return o
    
    def makeQuery(self, queryInfo):
        # Hard code default to querying Results
        if not queryInfo.has_key('queryType'): queryInfo['queryType'] = 'inspection'
        
        # Hard code to query the first object of type queryTYpe
        if not queryInfo.has_key('name'):
            if queryInfo['queryType'] == 'measurement':
                queryInfo['id'] = Measurement.objects[0].id
            elif queryInfo['queryType'] == 'inspection':
                queryInfo['id'] = Inspection.objects[0].id 
            else:
                log.warn('Unknown query type provided to OLAP Factory: ' + queryInfo['queryType'])
        
        # Limit of 1000
        if not queryInfo.has_key('limit'): queryInfo['limit'] = None
        
        return queryInfo
        
    def makeDesc(self, descInfo):
        # By default, assume that they want a median, grouped by minute, dropping partials
        if not descInfo.has_key('formula'): descInfo['formula'] = 'median'
        if not descInfo.has_key('window'): descInfo['window'] = 60
        if not descInfo.has_key('partial'): descInfo['partial'] = 'drop'
        
        return descInfo
        
    def makeTrans(self, transInfo):
        # Assume no transformations
        if not transInfo.has_key('norm'): transInfo['norm'] = 0
        if not transInfo.has_key('devFromMedian'): transInfo['devFromMedian'] = 0
        if not transInfo.has_key('devFromBase'): transInfo['devFromBase'] = 0
        if not transInfo.has_key('base'): transInfo['base'] = 0
        
        return transInfo

    def makeChart(self, chartInfo):
        if not chartInfo.has_key('chartColor'): chartInfo['chartColor'] = ''
        if not chartInfo.has_key('chartType'): chartInfo['chartType'] = 'line'
        # TODO: This is just for reverse compatibility.  It needs to go away
        if not chartInfo.has_key('name'): chartInfo['name'] = 'line'
        
        return chartInfo

    def calcInterval(self, dataSet, allow):
        xvals, rest = np.hsplit(np.array(dataSet), [1])
        
        # Time range for the points
        rangePoints = xvals[-1] - xvals[0]
        log.info('time range: ' + str(rangePoints))
        
        # Find new interval
        scaleRange = rangePoints / allow
        log.info('scale: ' + str(scaleRange))
        
        scaleRange = round(scaleRange)
        if (scaleRange < 1): scaleRange = 1
        
        scaleRange = int(scaleRange)
        
        # Round that up to the nearest round unit of time
        if scaleRange < 5: return 5
        elif scaleRange < 10: return 10 # 10 seconds
        elif scaleRange < 15: return 15 # 15 seconds
        elif scaleRange < 60: return 60 # 1 minute
        elif scaleRange < 300: return 300 # 5 minutes
        elif scaleRange < 600: return 600 # 10 minutes
        elif scaleRange < 900: return 900 # 15 minutes
        elif scaleRange < 3600: return 3600 # 1 hour
        elif scaleRange < 7200: return 7200 # 2 hours
        elif scaleRange < 14400: return 14400 # 4 hours
        elif scaleRange < 21600: return 21600 # 6 hours
        elif scaleRange < 86400: return 86400 # 1 day
        elif scaleRange < 604800: return 604800 # 1 week
        else: return scaleRange
    	
        return scaleRange
        	
class Chart:
    # Takes the data and puts it in a format for charting
    
    def dataRange(self, dataSet):
	# compute the min and max values suggested for the chart drawing
		ranges = dict()
	
		yvals = np.hsplit(np.array(dataSet),[1,2])[1]
		if (len(yvals) > 0):
			std = np.std(yvals)
			mean = np.mean(yvals)
			
			minFound = np.min(yvals)
			
			ranges['max'] = int(mean + 3*std)
			ranges['min'] = int(mean - 3*std)
			
			if (minFound > 0) and (ranges['min'] < 0): ranges['min'] = 0
		else:
			ranges['max'] = 0
			ranges['min'] = 0
		
		return ranges
    
    
    def createChart(self, resultSet, chartInfo, olapName = ''):
        # This function will change to handle the different formats
        # required for different charts.  For now, just assume nice
        # graphs of (x,y) coordiantes
        
        chartRange = self.dataRange(resultSet['data'])
        
        chartData = { 'chartType': chartInfo['name'],
                      'chartColor': chartInfo['color'],
                      'labels': resultSet['labels'],
                      'range': chartRange,
                      'data': resultSet['data'],
                      'olap': olapName }
        
        return chartData


class DescriptiveStatistic:

    _descInfo = {}
    
    def execute(self, resultSet, descInfo):
        self._descInfo = descInfo
      
        # Moving Average
        if (descInfo['formula'] == 'moving'):
            resultSet['data'] = self.movingAverage(resultSet['data'], descInfo['window'])
            resultSet['labels']['dim1'] = str(descInfo['window']) + ' Measurement Moving Average'
        # Mean
        elif (descInfo['formula'] == 'mean'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], np.mean)
            resultSet['labels']['dim1'] = 'Mean, group by ' + self.epochToText(descInfo['window'])
        # Median
        elif (descInfo['formula'] == 'median'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], np.median)
            resultSet['labels']['dim1'] = 'Median, group by ' + self.epochToText(descInfo['window'])
        # Mode
        elif (descInfo['formula'] == 'mode'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], self.mode)
            resultSet['labels']['dim1'] = 'Mode, group by ' + self.epochToText(descInfo['window'])
        # Variance
        elif (descInfo['formula'] == 'var'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], np.var)
            resultSet['labels']['dim1'] = 'Variance, group by ' + self.epochToText(descInfo['window'])
        # Standard Deviation
        elif (descInfo['formula'] == 'std'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], np.std)
            resultSet['labels']['dim1'] = 'Standard Deviation, group by ' + self.epochToText(descInfo['window'])
        # Max
        elif (descInfo['formula'] == 'max'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], np.max)
            resultSet['labels']['dim1'] = 'Maximum, group by ' + self.epochToText(descInfo['window'])
        # Min
        elif (descInfo['formula'] == 'min'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], np.min)
            resultSet['labels']['dim1'] = 'Minimum, group by ' + self.epochToText(descInfo['window'])
        # First
        elif (descInfo['formula'] == 'first'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], self.first)
            resultSet['labels']['dim1'] = 'First, group by ' + self.epochToText(descInfo['window'])
        # Last
        elif (descInfo['formula'] == 'last'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], self.last)
            resultSet['labels']['dim1'] = 'Last, group by ' + self.epochToText(descInfo['window'])
        # Lower Quartile
        elif (descInfo['formula'] == 'lq'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], self.lq)
            resultSet['labels']['dim1'] = 'Lower Quartile, group by ' + self.epochToText(descInfo['window'])
        # Upper Quartile
        elif (descInfo['formula'] == 'uq'):
            resultSet['data'] = self.binStatistic(resultSet['data'], descInfo['window'], self.uq)
            resultSet['labels']['dim1'] = 'Upper Quartile, group by ' + self.epochToText(descInfo['window'])
        
        return resultSet

    def movingAverage(self, dataSet, window):
        # Just return the raw data if window too big
        if (len(dataSet) < window):
            return dataSet
            
        # Right now, hard code to do the average on the second dimension (y vals)
        xvals, yvals, ids = np.hsplit(np.array(dataSet), [1,2])
        weights = np.repeat(1.0, window) / window
        yvals = np.convolve(yvals.flatten(), weights)[window-1:-(window-1)]
        xvals = xvals[window-1:]
        ids = ids[window-1:]

        dataSet = np.hstack((xvals, yvals.reshape(len(xvals),1), ids)).tolist()
        return dataSet

    def mode(self, x):
        # A little hack since the related SciPy function returns unnecessary data
        from scipy import stats
        return stats.mode(x)[0][0][0]
        
    def first(self, x):
        # First element of the series
        return x[0][0]
        
    def last(self, x):
        # Last element of the series
        return x[-1][0]
    
    def lq(self, x):
        # The lower quartile/25th percentile
        from scipy import stats
        return stats.scoreatpercentile(x, 25)[0]
        
    def uq(self, x):
        # The upper quartile/75th percentile
        from scipy import stats
        return stats.scoreatpercentile(x, 75)[0]
    

    def binStatistic(self, dataSet, groupBy, func):
        # Computed the indicated statistic (func) on each bin of data set
        
        # First trim the partial times on each end (unless told not to)
        if (not self._descInfo.has_key('trim')) or (self._descInfo['trim'] == 1):
            dataSet = self.trimData(dataSet, groupBy)
            
        if (len(dataSet) == 0):
            log.warn('Dataset trimmed to nothing')
            return dataSet
            
        # Group the data into bins
        [binSet, bins] = self.binData(dataSet, groupBy)
        
        numBins = len(bins)
        
        means = []
        objectids = []
        
        # Compute the means for each set of bins
        for b in binSet:
            xvals, yvals, ids = np.hsplit(np.array(b), [1,2])
            if (len(yvals) > 0):
                means.append(func(yvals)) 
                objectids.append(ids[-1].flatten())
            else:
                means.append(0)
                objectids.append([None, None, None, None])

        #log.info(objectids)
        objs = np.array(objectids).reshape(numBins, 4).tolist()
        
        # Replace the old time (x) values with the bin value    
        dataSet = np.hstack((np.array(bins).reshape(numBins, 1), np.array(means).reshape(numBins, 1), objs)).tolist()
        return dataSet
    
    def binData(self, dataSet, groupBy):
        # Note: bins are defined by the maximum value of an item allowed in the bin
        
        minBinVal = int(dataSet[0][0] + groupBy)
        maxBinVal = int(dataSet[-1][0] + groupBy)
        
        # Round the time to the nearest groupBy interval
        minBinVal -= minBinVal % groupBy
        maxBinVal -= maxBinVal % groupBy
        
        # Find the number of bins and size per bin
        numBins = (maxBinVal - minBinVal) / groupBy + 1
        bins = range(minBinVal, maxBinVal + 1, groupBy)
        
        # Identify which x values should appear in each bin
        xvals, rest = np.hsplit(np.array(dataSet), [1])
        # Hack to change xvals from type object to int
        xvals = np.array(xvals.flatten().tolist())
        inds = np.digitize(xvals, bins)

        # Put each data element i nits appropriate bin
        binified = [ [] for x in bins ]        
        for binNum, val in zip(inds, dataSet):
            binified[binNum].append(val)
        
        # Return the bin-ified original data and the bin labels (values)    
        return [binified, bins]
        
    def trimData(self, dataSet, groupBy):
        # Remove the fractional (minute, hour, day) from the beginning and end of the dataset
        
        startTime = dataSet[0][0] + groupBy
        endTime = dataSet[-1][0]
        
        # Round the time to the nearest groupBy interval
        startTime -= (startTime % groupBy)
        endTime -= (endTime % groupBy)
        
        # Filter out the beginning
        dataArr = np.array(dataSet)
        dataArr = dataArr[dataArr[0:len(dataArr),0:1].flatten() > startTime]
        # If anything left, filter out the end
        if len(dataArr) > 0: dataArr = dataArr[dataArr[0:len(dataArr),0:1].flatten() < endTime]
        
        return dataArr.tolist()
        
        
    def epochToText(self, groupBy):
        if groupBy < 60: return str(groupBy) + ' Second(s)'
        elif groupBy < 3600: return str(groupBy / 60) + ' Minute(s)'
        elif groupBy < 86400: return str(groupBy / 3600) + ' Hour(s)'
        elif groupBy < 604800: return str(groupBy / 86400) + ' Day(s)'
        else: return str(groupBy / 604800) + ' Week(s)'




class RealtimeOLAP:

    def realtime(self, res):
        olaps = OLAP.objects
        for o in olaps:
            
            # First, check for entries that just want the raw data
            # (If no descInfo is set or if descInfo lacks a formula field)
            if (o.descInfo is None) or (not o.descInfo.has_key('formula')):
                r = ResultSet()
                rset = r.resultToResultSet(res)
                self.sendMessage(o, rset['data'])

            elif o.descInfo['formula'] == 'moving':
                # Special case for the moving average
                # TODO: This goes through the unnecessary step of putting together chart params.  
                # Could optimize by just doing data steps
                
                o.queryInfo['limit'] = o.descInfo['window']
                rset = o.execute()
                self.sendMessage(o, rset['data'])
                
            else:
                # Trigger a descriptive if the previous record was on the other side of a group by window/interval
                window = o.descInfo['window']
                thisTime = calendar.timegm(res.capturetime.timetuple())
                previousTime = self.lastResult()
                border = thisTime - (thisTime % window)
                
                if (previousTime < border):
                    # This does the unnecessary step of creating chart info.  Could optimize this.
                    # log.info('Sending descriptive for ' + o.name)
                    o.descInfo['trim'] = 0
                    rset = o.execute(sincetime = border - window)
                    self.sendMessage(o, rset['data'])
                    
                
    def lastResult(self):
        # Show the timestamp of the last entry in the result table
        rs = Result.objects.order_by('-capturetime')
        return calendar.timegm(rs[0].capturetime.timetuple())

    def sendMessage(self, o, data):
        msgdata = [dict(
            id = str(o.id),
            data = d[0:2],
            inspection_id =  str(d[2]),
            frame_id = str(d[3]),
            measurement_id= str(d[4]),
            result_id= str(d[5])
        ) for d in data]
        
        #log.info('pushing new data to ' + utf8convert(o.name) + ' _ ' + str(msgdata))
        
        # Channel naming: OLAP/olap_name
        olapName = 'OLAP/' + utf8convert(o.name) + '/'
        ChannelManager().publish(olapName, dict(u='data', m=msgdata))


        
class ResultSet:    
    # Class to retrieve data from the database and add basic metadata
    
    
    def execute(self, queryInfo):
        # Execute the querystring, returning the results of the
        # query as a list
        
        
        # TODO: Select from the right type of object, not all
        if (queryInfo['queryType'] == 'inspection'):
            obj = Inspection
        elif (queryInfo['queryType'] == 'measurement'):
            obj = Measurement
        
        query = dict()
        if not queryInfo.has_key('id'):
            insp = obj.objects.get(name=queryInfo['name'])
            query[queryInfo['queryType']] = insp.id
        else:
            query[queryInfo['queryType']] = queryInfo['id']
            
        if queryInfo['since']:
            query['capturetime__gt']= datetime.utcfromtimestamp(queryInfo['since'])
        if queryInfo['before']:
            query['capturetime__lt']= datetime.utcfromtimestamp(queryInfo['before'])
        
        
        # Only truncate if a limit was set
        if (queryInfo['limit']):
            rs = list(Result.objects(**query).order_by('-capturetime')[:queryInfo['limit']])
        else:
            rs = list(Result.objects(**query).order_by('-capturetime'))
            
        
        # When performing some computations, require additional data
        if (len(rs) > 0) and (queryInfo.has_key('required')) and (len(rs) < queryInfo['required']):
        
            # If not, relax the capture time but only take the num records required
            del(query['capturetime__gt'])
            rs = list(Result.objects(**query).order_by('-capturetime')[:queryInfo['required']])
        
        outputVals = [[calendar.timegm(r.capturetime.timetuple()) + r.capturetime.time().microsecond / 1000000.0, r.numeric, r.inspection, r.frame, r.measurement, r.id] for r in rs[::-1]]
        
        
        if (len(outputVals) > 0):
            startTime = outputVals[0][0]
            endTime = outputVals[-1][0]
        else:
            startTime = 0
            endTime = 0
        
        #our timestamps are already in UTC, so we need to use a localtime conversion
        dataset = { 'startTime': startTime,
                    'endTime': endTime,
                    'timestamp': gmtime(),
                    'labels': {'dim0': 'Time', 'dim1': 'Motion', 'dim2': 'InspectionID', 'dim3': 'FrameID', 'dim4':'MeasurementID', 'dim5': 'ResultID'},
                    'data': outputVals}
                    
        return dataset
    
    
    def resultToResultSet(self, r):
        # Given a Result, format the Result like a one record ResultSet
        outputVals = [[calendar.timegm(r.capturetime.timetuple()) + r.capturetime.time().microsecond / 1000000.0, r.numeric, r.inspection, r.frame, r.measurement, r.id]]
        dataset = { 'startTime': outputVals[0][0],
                    'endTime': outputVals[0][0],
                    'timestamp': gmtime(),
                    'labels': {'dim0': 'Time', 'dim1': 'Motion', 'dim2': 'InspectionID', 'dim3': 'FrameID', 'dim4':'MeasurementID', 'dim5': 'ResultID'},
                    'data': outputVals}
        
        return dataset 



class Transform:
    
    _transInfo = dict()
    
    def transform(self, transInfo, dataSet):
        
        self._transInfo = transInfo
        
        xvals, yvals, ids = np.hsplit(np.array(dataSet), [1,2])
        
        # Test if needs to be normalized
        if (transInfo['normalize']):
            yvals = self.norm(yvals)
            
        # Test if reported as deviations from median
        if (transInfo['devFromMedian']):
            yvals = self.devFromMed(yvals)
            
        # Test if reported as deviations from specified value    
        if (transInfo['devFromBase']):
            if transInfo.has_base('base'):
                base = transInfo['base']
            else:
                base = 0
                
            yvals = self.devFromBase(yvals, base)
    
        dataSet = np.hstack((xvals.reshape(len(xvals), 1), yvals.reshape(len(yvals), 1),  ids.reshape(len(ids), 4))).tolist()
        return dataSet
    
    def norm(self, x):
        # Normalize the results to [0, 1]
        
        # Keep a cache of the bounds
        # TODO: Don't like this approach to caching and needing to save
        if not self._transInfo.has_key('lastMin'): self._transInfo['lastMin'] = min(x)[0]
        if not self._transInfo.has_key('lastMax'): self._transInfo['lastMax'] = max(x)[0]
        
        # The actual normalization
        normed = (x  - self._transInfo['lastMin']) / self._transInfo['lastMax'] 
            
        if (min(normed) < 0) or (max(normed) > 1):
            # When working off cached values for rounds, could create problems
            # For now, just write a warning to the log
            log.warn('Normalized date outside [0, 1]')
            
        return normed
            
        
    def devFromMed(self, x):
        # Standard deviations from the median
        return (x - np.median(x)) / float(np.std(x))
        
    def devFromBase(self, x, base):
        # Standard deviations from a specified base value
        return (x - base) / float(np.std(x))
    
