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
# allow: number of records after which triggering automatic aggregation: THIS WILL CHANGE SOON
# aggregate: the descriptive statistic to use for the automatic aggregation: THIS WILL CHANGE SOON 
#################################

class OLAPSchema(fes.Schema):
    name = fev.UnicodeString(not_empty=True)            
    queryInfo = V.JSON(not_empty=True)                  
    descInfo = V.JSON(if_empty=None, if_missing=None)   
    chartInfo = V.JSON(not_empty=True)
    transInfo = V.JSON(if_empty=None, if_missing=None)
    allow = fev.Int(if_missing=None)
    aggregate = fev.OneOf(['moving', 'mean', 'median', 'mode', 'var', 'std', 'max', 'min', 'first', 'last', 'uq', 'lq'], if_missing=None)

    
#################################
# queryType: defines the type of objects to be queries (inspections, measurements, results
# name: name of the object to lookup (object type defined by queryType)
# since: show only results with timestamp strictly greater than this time
# limit: limit the results returned to this number (by default, these are ordered by capture time)
#################################
  
class QueryInfoSchema(fes.Schema):
    objType = fev.OneOf(['inspection', 'measurement'], if_missing='inspection')
    objName = fev.UnicodeString(not_empty = True)
    objId = fev.UnicodeString(if_empty=None, if_missing=None)
    objFields = fev.Set(if_empty=None, if_missing=None)
    since = V.DateTime(if_empty=0, if_missing=None)
    before = V.DateTime(if_empty=0, if_missing=None)
    required = fev.Int(if_missing=None)
    limit = fev.Int(if_missing=None)
    

#################################
# formula: the descriptive statistic to apply
# window: the time interval for grouping for the statistic, expressed in epoch seconds
# EXCEPTION: window for moving average currently does number of records, not time interval
# partial: how to handle results from incomplete time intervals (e.g., new data 30 seconds into a one minute interval)
# TODO: partial not yet implemented.  Currently just drops partial
#################################

class DescInfoSchema(fes.Schema):
    formula = fev.OneOf(['moving', 'mean', 'median', 'mode', 'var', 'std', 'max', 'min', 'first', 'last', 'uq', 'lq', 'count'], if_missing=None)
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
# name: the style of chart to draw (e.g., bar, pie, etc)
# color: the color of the lines in the chart
# TODO, color should maybe be validated to a hex string or web color
#################################

class ChartInfoSchema(fes.Schema):
    name = fev.OneOf(['line', 'bar', 'pie', 'spline', 'area', 'areaspline','column','scatter'])
    color = fev.UnicodeString(if_empty="")
    minval = fev.Int(if_missing=None, if_empty=None)
    maxval = fev.Int(if_missing=None, if_empty=None)
    maxval = fev.Int(if_missing=None, if_empty=None)

        

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
    realtime = mongoengine.IntField()
    
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
        if (len(resultSet['data']) > self.allow):
            of = OLAPFactory()
            self = of.fromBigOLAP(self, resultSet)
            
            # Redo the descriptive with the new aggregation
            d = DescriptiveStatistic()
            resultSet = d.execute(resultSet, self.descInfo)
        
            
        #TODO: Re-integrate transformations here
        
        # Create and return the chart
        c = Chart()
        chartSpec = c.createChart(resultSet, self.chartInfo, self.name, self.realtime)
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
        
        # NOTE: this will clobber the aggregation function for moving average
        
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
        
            o.realtime = 0
        
            #similar = OLAP.objects.filter(name=o.name)
            #if (len(similar) == 0):
            #    log.info('made a new olap for aggregation: ' + o.name)
            #    o.save()
            #else:
            #    log.info('switching to olap: ' + o.name)
            #    o = similar[0]
            
        return o
    
    def makeOLAP(self, queryInfo = dict(), descInfo = dict(), transInfo = dict(), chartInfo = dict()):
    
        # Makes a generic OLAP with default values
        # If any values are provided as parameters, keeps those and fills in the rest
    
        o = OLAP()
        o.queryInfo = self.makeQuery(queryInfo)
        o.descInfo = self.makeDesc(descInfo)
        o.transInfo = self.makeTrans(transInfo)
        o.chartInfo = self.makeChart(chartInfo)
        
        if not o.allow: o.allow = 900
        if not o.aggregate: o.aggregate = 'median'
        if o.descInfo:
            o.name = o.queryInfo['objType'] + o.descInfo['formula'] + str(o.descInfo['window'])
        else:
            o.name = o.queryInfo['objType'] + str(o.queryInfo['objName']) + str(o.queryInfo['objId'])
        
        
        
        return o
    
    def makeQuery(self, queryInfo):
        # Hard code default to querying Results
        if not queryInfo.has_key('objType'): queryInfo['queryType'] = 'inspection'
        
        # Hard code to query the first object of type queryTYpe
        if not queryInfo.has_key('objName'):
            queryInfo['objName'] = None
            if queryInfo['objType'] == 'measurement':
                queryInfo['objId'] = Measurement.objects[0].id
            elif queryInfo['objType'] == 'inspection':
                queryInfo['objId'] = Inspection.objects[0].id 
            else:
                log.warn('Unknown query type provided to OLAP Factory: ' + queryInfo['objType'])
        else:
            queryInfo['objId'] = None
            
        if not queryInfo.has_key('objFields'): queryInfo['objFields'] = ['capturetimeEpochMS', 'numeric', 'inspection', 'frame', 'measurement', 'id']
        
        # Limit of 1000
        if not queryInfo.has_key('limit'): queryInfo['limit'] = None
        if not queryInfo.has_key('required'): queryInfo['required'] = None
        if not queryInfo.has_key('before'): queryInfo['before'] = None
        if not queryInfo.has_key('since'): queryInfo['since'] = None
        
        return queryInfo
        
    def makeDesc(self, descInfo):
        # Don't create if was passed None
        # By default, assume that they want a median, grouped by minute, dropping partials
        if not descInfo == None:
            if not descInfo.has_key('formula'): descInfo['formula'] = 'median'
            if not descInfo.has_key('window'): descInfo['window'] = 60
            if not descInfo.has_key('partial'): descInfo['partial'] = 'drop'
            if not descInfo.has_key('trim'): descInfo['trim'] = True
            if not descInfo.has_key('params'): descInfo['params'] = ['capturetimeEpochMS', 'numeric']
            if not descInfo.has_key('minWindow'): descInfo['minWindow'] = None
            if not descInfo.has_key('maxWindow'): descInfo['maxWindow'] = None
            
        return descInfo
        
    def makeTrans(self, transInfo):
        # Assume no transformations
        if not transInfo.has_key('norm'): transInfo['norm'] = 0
        if not transInfo.has_key('devFromMedian'): transInfo['devFromMedian'] = 0
        if not transInfo.has_key('devFromBase'): transInfo['devFromBase'] = 0
        if not transInfo.has_key('base'): transInfo['base'] = 0
        
        return transInfo

    def makeChart(self, chartInfo):
        if not chartInfo.has_key('color'): chartInfo['color'] = 'blue'
        if not chartInfo.has_key('name'): chartInfo['name'] = 'line'
        if not chartInfo.has_key('minval'): chartInfo['minval'] = None
        if not chartInfo.has_key('maxval'): chartInfo['maxval'] = None
        if not chartInfo.has_key('xtype'): chartInfo['xtype'] = 'datetime'
        if not chartInfo.has_key('ticker'): chartInfo['ticker'] = None
        
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
    
    
    def createChart(self, resultSet, chartInfo, olapName = '', realtime = 1):
        # This function will change to handle the different formats
        # required for different charts.  For now, just assume nice
        # graphs of (x,y) coordiantes
        
        chartRange = {'max':0, 'min':0}
        # If missing either/both of the predefined chart range values
        if not chartInfo.has_key('minval') or not chartInfo.has_key('maxval'):
            chartRange = self.dataRange(resultSet['data'])
            
        # Override comptued values if they were defined
        if chartInfo['minval'] is not None: chartRange['min'] = chartInfo['minval']
        if chartInfo['maxval'] is not None: chartRange['max'] = chartInfo['maxval']
        
        chartData = { 'name': chartInfo['name'],
                      'color': chartInfo['color'],
                      'labels': resultSet['labels'],
                      'range': chartRange,
                      'data': resultSet['data'],
                      'olap': olapName,
                      'realtime': realtime,
                      'xtype': chartInfo['xtype'],
                      'ticker': chartInfo['ticker'] }
        
        return chartData


class DescriptiveStatistic:

    _descInfo = {}
    
    def execute(self, resultSet, descInfo):
        self._descInfo = descInfo

        data = resultSet['data']
        
        # Right now I'm still hard coding to two parameters (group, series)
        binIdx = resultSet['labels'].index(descInfo['params'][0])
        valIdx = resultSet['labels'].index(descInfo['params'][1])
      
        data.sort(key=lambda x: x[binIdx])
      
        dataArr = np.array(data)
        parts = np.hsplit(dataArr, len(dataArr[0]))
        
        group = parts[binIdx].flatten().tolist()
        series = parts[valIdx].flatten().tolist()
        
        # Remove the two main data points and track the rest of the meta data
        meta = parts
        del(meta[binIdx])
        
        # Adjust the index to delete based on the previous deletion
        delValIdx = valIdx
        if binIdx < valIdx: delValIdx -= 1
        del(meta[delValIdx])
        
        # Fix meta so each list element consists of a list of all the non-used entries per result
        meta = np.hstack((m for m in meta)).tolist()
        
        
        # Moving Average
        if (descInfo['formula'] == 'moving'):
            resultSet['data'] = self.assemble(self.movingAverage(group, series, meta, descInfo['window']))
            resultSet['labels'][valIdx] = str(descInfo['window']) + ' Measurement Moving Average'
        # Mean
        elif (descInfo['formula'] == 'mean'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], np.mean))
            resultSet['labels'][valIdx] = 'Mean, group by ' + self.epochToText(descInfo['window'])
        # Median
        elif (descInfo['formula'] == 'median'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], np.median))
            resultSet['labels'][valIdx] = 'Median, group by ' + self.epochToText(descInfo['window'])
        # Mode
        elif (descInfo['formula'] == 'mode'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], self.mode))
            resultSet['labels'][valIdx] = 'Mode, group by ' + self.epochToText(descInfo['window'])
        # Variance
        elif (descInfo['formula'] == 'var'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], np.var))
            resultSet['labels'][valIdx] = 'Variance, group by ' + self.epochToText(descInfo['window'])
        # Standard Deviation
        elif (descInfo['formula'] == 'std'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], np.std))
            resultSet['labels'][valIdx] = 'Standard Deviation, group by ' + self.epochToText(descInfo['window'])
        # Max
        elif (descInfo['formula'] == 'max'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], np.max))
            resultSet['labels'][valIdx] = 'Maximum, group by ' + self.epochToText(descInfo['window'])
        # Min
        elif (descInfo['formula'] == 'min'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], np.min))
            resultSet['labels'][valIdx] = 'Minimum, group by ' + self.epochToText(descInfo['window'])
        # First
        elif (descInfo['formula'] == 'first'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], self.first))
            resultSet['labels'][valIdx] = 'First, group by ' + self.epochToText(descInfo['window'])
        # Last
        elif (descInfo['formula'] == 'last'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], self.last))
            resultSet['labels'][valIdx] = 'Last, group by ' + self.epochToText(descInfo['window'])
        # Lower Quartile
        elif (descInfo['formula'] == 'lq'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], self.lq))
            resultSet['labels'][valIdx] = 'Lower Quartile, group by ' + self.epochToText(descInfo['window'])
        # Upper Quartile
        elif (descInfo['formula'] == 'uq'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], self.uq))
            resultSet['labels'][valIdx] = 'Upper Quartile, group by ' + self.epochToText(descInfo['window'])
        elif (descInfo['formula'] == 'count'):
            resultSet['data'] = self.assemble(self.binStatistic(group, series, meta, descInfo['window'], self.count))
            resultSet['labels'][valIdx] = 'Count, group by ' + str(descInfo['window'])
        
        
        return resultSet

    def movingAverage(self, group, series, meta, window):
        # Just return the raw data if window too big/data series too small
        if (len(group) < window):
            return [group, series, meta]
            
        # Right now, hard code to do the average on the second dimension (y vals)
        weights = np.repeat(1.0, window) / window
        series = np.convolve(series, weights)[window-1:-(window-1)]
        group = group[window-1:]
        meta = meta[window-1:]
        
        # Can't pickle numpy.float64 objects, so convert them back to floats
        # TODO: Check if there is a better/faster way
        
        series = [ float(x) for x in series ]
        
        return [group, series, meta]

    def mode(self, x):
        # A little hack since the related SciPy function returns unnecessary data
        from scipy import stats
        return stats.mode(x)[0][0]
        
    def first(self, x):
        # First element of the series
        return x[0]
        
    def last(self, x):
        # Last element of the series
        return x[-1]
    
    def lq(self, x):
        # The lower quartile/25th percentile
        from scipy import stats
        return stats.scoreatpercentile(x, 25)
        
    def uq(self, x):
        # The upper quartile/75th percentile
        from scipy import stats
        return stats.scoreatpercentile(x, 75)
        
    def count(self, x):
        return len(x)
    

    def binStatistic(self, group, series, meta, window, func):
        # Computed the indicated statistic (func) on each bin of data set
        
        # First trim the partial times on each end (unless told not to)
        if self._descInfo['trim']:
            [group, series, meta] = self.trimData(group, series, meta, window)
        
        if (len(group) == 0):
            log.warn('Dataset trimmed to nothing')
            return [], [], []
            
        # Group the data into bins
        [binSet, bins] = self.binData(group, series, meta, window)
        
        numBins = len(bins)
        
        newSeries = []
        newMeta = []
        
        # Compute the stats for each set of bins
        for b in binSet:
            g, s, m = b
            if (len(g) > 0):
                newSeries.append(float(func(s))) 
                newMeta.append(m[-1])
            else:
                newSeries.append(0)
                newMeta.append([None, None, None, None])

        return [bins, newSeries, newMeta]
    
    def binData(self, group, series, meta, window):
        # Note: bins are defined by the maximum value of an item allowed in the bin
        
        if self._descInfo['minWindow']:
            minBinVal = self._descInfo['minWindow']
        else:
            minBinVal = int(group[0] + window)
        
        if self._descInfo['maxWindow']:
            maxBinVal = self._descInfo['maxWindow']
        else:
            maxBinVal = int(group[-1] + window)
    
        # Round the time to the nearest groupBy interval
        minBinVal -= minBinVal % window
        maxBinVal -= maxBinVal % window
        
        # Find the number of bins and size per bin
        numBins = (maxBinVal - minBinVal) / window + 1
        bins = range(minBinVal, maxBinVal + 1, window)
        
        # Identify which x values should appear in each bin
        # Note: use tolist() to convert to a numeric type instead of object
        group = np.array(group)
        idxs = np.digitize(group, bins)

        # This is a temporary check.  Should be removed when bug fixed
        maxIdx = max(idxs)
        binLen = len(bins)
        if (maxIdx > (binLen - 1)):
            log.warn('Error in computing bin length')
            log.warn('Min bin ' + str(minBinVal))
            log.warn('Max bin ' + str(maxBinVal))
            log.warn('Min Window ' + str(descInfo['minWindow']))
            log.warn('Max Window ' + str(descInfo['maxWindow']))
            log.warn('Window size ' + str(window))
            log.warn('Max Index ' + str(maxIdx))
            log.warn('Number of bins ' + str(binLen))
            
            # Quick hack to fix
            binLen += 1
            
            

        # Put each data element i nits appropriate bin
        # Need a list element for each bin.  Each of those lists needs three more lists for group, series, meta
        binified = [ [ [], [], [] ] for x in bins ]        
        for idx, g, s, m in zip(idxs, group, series, meta):
            binified[idx][0].append(g)
            binified[idx][1].append(s)
            binified[idx][2].append(m)
        
        # Return the bin-ified original data and the bin labels (values)    
        return [binified, bins]
        
    def trimData(self, group, series, meta, window):
        # Remove the fractional (minute, hour, day) from the beginning and end of the dataset
        
        startTime = group[0] + window
        endTime = group[-1]
        
        # Round the time to the nearest groupBy interval
        startTime -= (startTime % window)
        endTime -= (endTime % window)
        
        # Filter out the beginning and end
        
        groupFilt = []
        seriesFilt = []
        metaFilt = []
        
        for g, s, m in zip(group, series, meta):
            if g >= startTime and g <= endTime:
                groupFilt.append(g)
                seriesFilt.append(s)
                metaFilt.append(m)
    
        return [groupFilt, seriesFilt, metaFilt]
        
        
    def epochToText(self, groupBy):
        if groupBy < 60: return str(groupBy) + ' Second(s)'
        elif groupBy < 3600: return str(groupBy / 60) + ' Minute(s)'
        elif groupBy < 86400: return str(groupBy / 3600) + ' Hour(s)'
        elif groupBy < 604800: return str(groupBy / 86400) + ' Day(s)'
        else: return str(groupBy / 604800) + ' Week(s)'

    def assemble(self, parts):
        g, s, m = parts
        combined = [ [a, b] + c for a, b, c in zip(g, s, m) ]
        return combined



class RealtimeOLAP:

    def realtime(self, res):
        olaps = OLAP.objects
        for o in olaps:
            
            # First, check for entries that just want the raw data
            # (If no descInfo is set or if descInfo lacks a formula field)
            if (o.descInfo is None) or (not o.descInfo.has_key('formula')):
                r = ResultSet()
                rset = r.resultToResultSet(o.queryInfo, res)
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
        if len(rs) > 0: 
            return calendar.timegm(rs[0].capturetime.timetuple())
        else:
            return 0

    def sendMessage(self, o, data):
        if (len(data) > 0):
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
        # Execute the query, returning the results of the as a list
        
        # Get the object type that will be queried
        if (queryInfo['objType'] == 'inspection'):
            Obj = Inspection
        elif (queryInfo['objType'] == 'measurement'):
            Obj = Measurement
        else:
            log.warn('Incorrect objType defined.  Defaulting to inspection.')
            queryInfo['objType'] = 'inspection'
            Obj = Inspection
            
            
        # Setup the query parameters
        query = dict()
        
        # First, find the ID of the type of object to be queried for
        # If the name was provided instead of the ID, lookup the ID
        if not queryInfo['objId'] and queryInfo['objName']:
            objs = Obj.objects.filter(name=queryInfo['objName'])
        else:
            objs = Obj.objects.filter(id = queryInfo['objId'])
        
        # Make sure working with only a unique object
        if (len(objs) == 1):
            thisObj = objs[0]
            query[queryInfo['objType']] = thisObj.id
        elif (len(objs) > 1):
            log.warn('Too many objects returned on ' + queryInfo['objType'] + '/' + queryInfo['objName'] + '/' + queryInfo['objId'])
            log.warn('Using just the first result')
            thisObj = objs[0]
            query[queryInfo['objType']] = thisObj.id
        else:
            log.warn('No objects returned found on ' + queryInfo['objType'] + '/' + queryInfo['objName'] + '/' + queryInfo['objId'])
            return []
            
        # Restrict to only results after 'since' timestamp    
        if queryInfo['since']:
            query['capturetime__gt']= datetime.utcfromtimestamp(queryInfo['since'])
        
        # Restrict to only results preceding 'before' timestamp
        if queryInfo['before']:
            query['capturetime__lt']= datetime.utcfromtimestamp(queryInfo['before'])
        
        # If a custom filter was defined
        if queryInfo.has_key('filter'):
            filt = queryInfo['filter']
            query[filt['field']] = filt['val']
        
        # Get the results
        # Only truncate if a limit was set
        if (queryInfo['limit']):
            rs = list(Result.objects(**query).order_by('-capturetime')[:queryInfo['limit']])
        else:
            rs = list(Result.objects(**query).order_by('-capturetime'))
            
        
        # When performing some computations, require additional data
        # E.g., moving averages may require a series of earlier points
        if (len(rs) > 0) and (queryInfo.has_key('required')) and (len(rs) < queryInfo['required']):
            # If not, relax the capture time but only take the num records required
            del(query['capturetime__gt'])
            rs = list(Result.objects(**query).order_by('-capturetime')[:queryInfo['required']])
        
        
        # Setup the list of fields to retrieve
        params = queryInfo['objFields']
        
        # We need a timestamp for other calculations, so make sure it is always present in requested parameters
        if not 'capturetimeEpochMS' in params:
            params.append('capturetimeEpochMS')
        
        
        # Get the list of result values
        outputVals = [[r.__getattribute__(p) for p in params] for r in rs[::-1]]
        
        rounds = queryInfo['round']
        for i in range(len(params)):
            if rounds[i] is not None:
                for o in outputVals:
                    o[i] = o[i] - o[i] % rounds[i]  

        # The purple pass/fail test
        if queryInfo.has_key('passfail'):
            for o in outputVals:
                if (o[1] == 'purple'):
                    o[1] = 0
                else:
                    o[1] = 1
                    
        if queryInfo.has_key('cton'):
            for o in outputVals:
                if o[1] == 'red':
                    o[1] = '0'
                elif o[1] == 'green':
                    o[1] = '1'
                if o[1] == 'yellow':
                    o[1] = '2'
                if o[1] == 'orange':
                    o[1] = '3'
                if o[1] == 'purple':
                    o[1] = '4'
                if o[1] == 'blue':
                    o[1] = '5'
                    
        
        # Some results may be in string of tupletime.  Convert to epoch
        # Nate is working on better fix
        if queryInfo.has_key('fixdate'):
            for o in outputVals:
                if (type(o[1]) == unicode):
                    tup = o[1].split(':')
                    o[1] = float(tup[0]) * 3600 + float(tup[1]) * 60 + float(tup[2])
                        
        
        # Track the start and end time of the resultset
        idx = params.index('capturetimeEpochMS')
        if (len(outputVals) > 0):
            startTime = outputVals[0][idx]
            endTime = outputVals[-1][idx]
        else:
            startTime = 0
            endTime = 0
        
        # Construct the final resultset data
        dataset = { 'startTime': startTime,
                    'endTime': endTime,
                    'labels': params,
                    'data': outputVals}
                    
        return dataset
    
    
    def resultToResultSet(self, queryInfo, r):
        # Given a Result, format the Result like a one record ResultSet
        
        # Setup the list of fields to retrieve
        params = queryInfo['objFields']
        
        # We need a timestamp for other calculations, so make sure it is always present in requested parameters
        if not 'capturetimeEpochMS' in params:
            params.append('capturetimeEpochMS')
        
        # Construct the list from params the the provided result 
        
        outputVals = [[r.__getattribute__(p) for p in params]]
        
        rounds = queryInfo['round']
        for i in range(len(params)):
            if rounds[i] is not None:
                for o in outputVals:
                    if o[i] is not None:
                        o[i] = o[i] - o[i] % rounds[i]

        idx = params.index('capturetimeEpochMS')        
        dataset = { 'startTime': outputVals[0][idx],
                    'endTime': outputVals[0][idx],
                    'timestamp': gmtime(),
                    'fields': params,
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
    
    
class Inferential:
    
    def recentEventStats(resultSet, thresh):
        endTime = self.recentEventEnd(resultSet, thresh)
        startTime = self.recentEventStart(resultSet, endTime, thresh)
        mag = self.recentEventMagnitue(resultToResultSet, startTime, endTime)
        
        return [startTime, endTime, mag]
    
    def recentEventEnd(resultSet, thresh):
        return 0
        
    def recentEvenStart(resultSet, end, thresh):
        return 0
        
    def recentEventMagnitue(resultSet, start, end):
        return 0
