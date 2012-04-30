import base
from base import *
from Session import Session
from Inspection import Inspection
from Result import Result
from time import gmtime
import random
import calendar
from datetime import datetime as dt
import numpy as np

class OLAP(mongoengine.Document, base.SimpleDoc):
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
	timeStamp = mongoengine.DateTimeField()
	
	def __repr__(self):
		return "<OLAP %s>" % self.name
		
	def execute(self, sincetime = 0):
		# Get the resultset
		# Currently assume only one query (which will give random data)
		r = ResultSet()
		
		queryinfo = self.queryInfo.copy()
		if sincetime > 0:
			queryinfo['since'] = sincetime
		
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
	
	def createChart(self, resultSet, chartInfo):
		# This function will change to handle the different formats
		# required for different charts.  For now, just assume nice
		# graphs of (x,y) coordiantes
		
		chartData = { 'chartType': chartInfo['name'],
					  'chartColor': chartInfo['color'],
					  'labels': resultSet['labels'],
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
		# query as a numpy vector
		#
		# Entering a 'random' querystring will return a matrix with
		# sequential x values and random y values between 0 and 1
		#
		# Entering 'inspection' will do a predefined query to return
		# inspection objects
		#
		# Other query handling deferred for another day.


		insp = Inspection.objects.get(name=queryInfo['name'])

		query = dict(inspection = insp.id)

		if queryInfo.has_key('since'):
			query['capturetime__gt']= dt.utcfromtimestamp(queryInfo['since'])

		rs = Result.objects(**query).order_by('capturetime')

		outputVals = [[calendar.timegm(r.capturetime.timetuple()), r.numeric] for r in rs]
		#our timestamps are already in UTC, so we need to use a localtime conversion
		
		dataset = { 'startTime': 'all',
						'endTime': 'all',
						'timestamp': gmtime(),
						'labels': {'dim1': 'Time', 'dim2': 'Motion'},
						'data': outputVals}
		
		return dataset
