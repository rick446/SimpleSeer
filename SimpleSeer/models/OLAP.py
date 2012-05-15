import calendar
from time import gmtime
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
        print limitresults
        print queryinfo['limit']
        
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
            cm.publish(channelName, dict(u='data', m=[rset['data']]))
        
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
            window = descInfo['window']
            
            # Just return the raw data if window too big
            if (len(resultSet['data']) < window):
                return resultSet
            
            # assume I want to do the averge on the second dimension
            xvals, yvals, ids = np.hsplit(np.array(resultSet['data']), [1,2])
            weights = np.repeat(1.0, window) / window
            yvals = np.convolve(yvals.flatten(), weights)[window-1:-(window-1)]
            xvals = xvals[window-1:]
            ids = ids[window-1:]
            
            resultSet['data'] = np.hstack((xvals, yvals.reshape(len(xvals),1), ids)).tolist()
            return resultSet

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
        # E.g., 5 period moving average means we need _limit_ data points, plus four more
        # Check if we got enough entries
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
	
