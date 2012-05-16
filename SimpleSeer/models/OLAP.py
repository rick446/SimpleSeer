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
import gevent as g
from SimpleSeer.util import utf8convert

from SimpleSeer import validators as V
from .base import SimpleDoc
from .Inspection import Inspection
from .Result import Result

log = logging.getLogger(__name__)


class OLAPSchema(fes.Schema):
    name = fev.UnicodeString(not_empty=True)
    queryInfo = V.JSON(not_empty=True)
    descInfo = V.JSON(if_empty=None, if_missing=None)
    chartInfo = V.JSON(not_empty=True)
  
class QueryInfoSchema(fes.Schema):
    name = fev.UnicodeString(not_empty = True)
    since = V.DateTime(if_empty=0, if_missing=None)
    
class DescInfoSchema(fes.Schema):
    formula = fev.OneOf(['moving', 'mean', 'std'], if_missing=None)
    window = fev.Int(if_missing=None)

class ChartInfoSchema(fes.Schema):
    chartType = fev.OneOf(['line', 'bar', 'pie', 'spline', 'area', 'areaspline','column','scatter'])
    chartColor = fev.UnicodeString(if_empty="")
    #TODO, this should maybe be validated to a hex string or web color

class OLAP(SimpleDoc, mongoengine.Document):
    # General flow designed for:
    # - One or more Queries to retrieve data from database
    # - Zero or more DescriptiveStatistics, computed from Queries
    # - One Cube, that merges data from Queries and DescriptiveStats
    # - Zero or more InferentialStatistics, computed from Cube
    # - One or more Chart, with the resuls from Cube or InferentialStats
    #
    # This class will handle most of the processing rather than 
    # Stepping through these manually.  Put a query string in one
    # end and the configuration and data for a chart will pop out 
    # the other end.

    name = mongoengine.StringField()
    queryInfo = mongoengine.DictField()
    descInfo = mongoengine.DictField()
    chartInfo = mongoengine.DictField()
        
    def __repr__(self):
        return "<OLAP %s>" % self.name
        
    def execute(self, sincetime = 0, limitresults = None):
        r = ResultSet()
        
        
        # Process configuration parameters
        queryinfo = self.queryInfo.copy()
        queryinfo['since'] = sincetime
        queryinfo['limit'] = self.limitResults(limitresults)
        
        # Get the resultset
        resultSet = r.execute(queryinfo)
        
        # Check if any descriptive processing
        if (self.descInfo):
            d = DescriptiveStatistic()
            resultSet = d.execute(resultSet, self.descInfo)
        
        # Create and return the chart
        c = Chart()
        chartSpec = c.createChart(resultSet, self.chartInfo)
        return chartSpec
        
    def realtime(self, cm):
        # Pull up the channel manager to handle publishing results
        
        channelName = utf8convert('OLAP')
        
        if (not self.queryInfo.has_key('limit')): self.queryInfo['limit'] = 500
        if (not self.queryInfo.has_key('since')): self.queryInfo['since'] = 0
        
        r = ResultSet()
        rset = r.execute(self.queryInfo)
        
        if len(rset['data']) > 0:
            # Check if any descriptive processing
            
            if (self.descInfo):
                d = DescriptiveStatistic()
                newrset = d.execute(rset, self.descInfo)
                
            # Push to the channel
            log.info('Publish %r', channelName)
            data = rset['data']
            msgdata = [dict(
                id = self.id,
                data = d[0:1],
                inspection_id =  str(d[2]),
                frame_id = d[3],
                measurement_id= d[4],
                result_id= d[5]
            ) for d in data]
            cm.publish(channelName, dict(u='data', m=msgdata))
        
            self.queryInfo['since'] = rset['data'][-1][0] + 1
        
    def limitResults(self, thelimit):
        # If provided a limit, always use that limit
        # Else, if not defined in OLAP, use 500
        # Otherwise, use the one defined in OLAP
        if thelimit:
			return thelimit
        elif not self.queryInfo.has_key('limit'):
			return 500
        
        return self.queryInfo['limit']
		
        
			
        
        
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
    
    def createChart(self, resultSet, chartInfo):
        # This function will change to handle the different formats
        # required for different charts.  For now, just assume nice
        # graphs of (x,y) coordiantes
        
        chartRange = self.dataRange(resultSet['data'])
        
        chartData = { 'chartType': chartInfo['name'],
                      'chartColor': chartInfo['color'],
                      'labels': resultSet['labels'],
                      'range': chartRange,
                      'data': resultSet['data'] }
        
        return chartData


class DescriptiveStatistic:
    # Will be used for computing basic descriptives on query results
    # (e.g., sums, counts, means, moving averages)

    # TODO: This is just a quick hack to make it work.  Future: make
    # more plugin-able and configurable
    
    def execute(self, resultSet, descInfo):
        if (descInfo['formula'] == 'moving'):
            resultSet['data'] = self.movingAverage(resultSet['data'], descInfo['window'])
            resultSet['labels']['dim1'] = str(descInfo['window']) + ' Measurement Moving Average'
        elif (descInfo['formula'] == 'mean'):
            resultSet['data'] = self.mean(resultSet['data'], descInfo['window'])
            resultSet['labels']['dim1'] = 'Average by ' + self.epochToText(descInfo['window'])
            
            
            
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
    
    def mean(self, dataSet, groupBy):
        # Compute a simple mean for the data, grouped in the interval specified in groupBy
        
        # First trim the partial time and put into bins
        trimSet = self.trimData(dataSet, groupBy)
        [binSet, bins] = self.binData(trimSet, groupBy)
        
        numBins = len(bins)
        
        means = []
        objectids = []
        
        # Compute the means for each set of bins
        for b in binSet:
            xvals, yvals, ids = np.hsplit(np.array(b), [1,2])
            if (len(yvals) > 0):
                means.append(np.mean(yvals)) 
                objectids.append(ids[-1].tolist())
            else:
                means.append(0)
                objectids.append([])
        
        # Replace the old time (x) values with the bin value    
        dataSet = np.hstack((np.array(bins).reshape(numBins, 1), np.array(means).reshape(numBins, 1), np.array(objectids).reshape(numBins, 1))).tolist()
        return dataSet
    
    def binData(self, dataSet, groupBy):
        # Note: bins are defined by the maximum value of an item allowed in the bin
        
        minBinVal = dataSet[0][0] + groupBy
        maxBinVal = dataSet[-1][0] + groupBy
        
        # Round the time to the nearest groupBy interval
        minBinVal -= (minBinVal % groupBy)
        maxBinVal -= (maxBinVal % groupBy)
        
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
        
        # Filter out the beginning and end
        dataArr = np.array(dataSet)
        dataArr = dataArr[dataArr[0:len(dataArr),0:1].flatten() > startTime]
        dataArr = dataArr[dataArr[0:len(dataArr),0:1].flatten() < endTime]
        
        return dataArr.tolist()
        
    def epochToTupleIndex(self, groupBy):
        if groupBy == 60: return 4      # minutes
        elif groupBy == 3600: return 3  # hours
        elif groupBy == 86400: return 2 # days

        # Assume the default is 5, which will basically cause nothing
        # to happen in the trim function
        return 5

    def epochToText(self, groupBy):
        if groupBy == 60: return 'Minute'
        elif groupBy == 3600: return 'Hour'
        elif groupBy == 86400: return 'Day'

        return 'Group Increment Error'

class ResultSet:    
    # Class to retrieve data from the database and add basic metadata
    
    
    def execute(self, queryInfo):
        # Execute the querystring, returning the results of the
        # query as a list
        #
        # Entering 'Motion' will do a predefined query to return
        # inspection objects
        #
        # Other query handling deferred for another day.

        insp = Inspection.objects.get(name=queryInfo['name'])
        query = dict(inspection = insp.id)
        
        if queryInfo.has_key('since'):
            query['capturetime__gt']= datetime.utcfromtimestamp(queryInfo['since'])

        rs = list(Result.objects(**query).order_by('-capturetime')[:queryInfo['limit']])
        
        # When performing some computations, require additional data
        if (len(rs) > 0) and (queryInfo.has_key('required')) and (len(rs) < queryInfo['required']):
            # If not, relax the capture time but only take the num records required
            del(query['capturetime__gt'])
            rs = list(Result.objects(**query).order_by('-capturetime')[:queryInfo['required']])
        
        outputVals = [[calendar.timegm(r.capturetime.timetuple()), r.numeric, r.inspection, r.frame, r.measurement, r.id] for r in rs[::-1]]
        
        
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
	
