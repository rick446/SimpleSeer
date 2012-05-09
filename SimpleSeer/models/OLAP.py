import calendar
from time import gmtime
from datetime import datetime

import mongoengine
import numpy as np

from .base import SimpleDoc
from .Inspection import Inspection
from .Result import Result

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
        
        queryinfo = self.queryInfo.copy()
        if sincetime > 0:
            queryinfo['since'] = sincetime
        
        # If provided a limit, always use that limit
        # Else, if not defined in OLAP, use 500
        # Otherwise, use the one defined in OLAP
        if limitresults:
			queryinfo['limit'] = limitresults
        elif not queryinfo.has_key('limit'):
			queryinfo['limit'] = 500
		
			
        resultSet = r.execute(queryinfo)
        
        # Check if any descriptive processing
        if (self.descInfo):
            d = DescriptiveStatistic()
            resultSet = d.execute(resultSet, self.descInfo)
        
        # Create and return the chart
        c = Chart()
        chartSpec = c.createChart(resultSet, self.chartInfo)
        return chartSpec
        

class Chart:
    # Takes the data and puts it in a format for charting
    
    def dataRange(self, dataSet):
	# compute the min and max values suggested for the chart drawing
		ranges = dict()
	
		yvals = np.hsplit(np.array(dataSet),2)[1]
		std = np.std(yvals)
		mean = np.mean(yvals)
		
		minFound = np.min(yvals)
		
		ranges['max'] = int(mean + 3*std)
		ranges['min'] = int(mean - 3*std)
		
		if (minFound > 0) and (ranges['min'] < 0): ranges['min'] = 0
		
		return ranges
    
    def createChart(self, resultSet, chartInfo):
        # This function will change to handle the different formats
        # required for different charts.  For now, just assume nice
        # graphs of (x,y) coordiantes
        
        chartRange = self.dataRange(resultSet['data'])
        print chartRange
        
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
            xvals, yvals = np.hsplit(np.array(resultSet['data']), 2)
            weights = np.repeat(1.0, window) / window
            yvals = np.convolve(yvals.flatten(), weights)[window-1:-(window-1)]
            xvals = xvals[window-1:]
            
            resultSet['data'] = np.hstack((xvals, yvals.reshape(len(xvals),1))).tolist()
            return resultSet

class ResultSet:    
    # Class to retrieve data from the database and return as
    # Numpy matrix
    
    
    def execute(self, queryInfo):
        # Execute the querystring, returning the results of the
        # query as a list
        #
        # Entering 'inspection' will do a predefined query to return
        # inspection objects
        #
        # Other query handling deferred for another day.


        insp = Inspection.objects.get(name=queryInfo['name'])

        query = dict(inspection = insp.id)

        if queryInfo.has_key('since'):
            query['capturetime__gt']= datetime.utcfromtimestamp(queryInfo['since'])

        rs = Result.objects(**query).order_by('capturetime')[len(Result.objects)-queryInfo['limit']:len(Result.objects)]

        outputVals = [[calendar.timegm(r.capturetime.timetuple()), r.numeric] for r in rs]
        #our timestamps are already in UTC, so we need to use a localtime conversion
        
        dataset = { 'startTime': outputVals[0][0],
                    'endTime': outputVals[-1][0],
                    'timestamp': gmtime(),
                    'labels': {'dim1': 'Time', 'dim2': 'Motion'},
                    'data': outputVals}
        
        return dataset
	

