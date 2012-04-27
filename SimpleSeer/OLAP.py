import base
from base import *
from Session import Session
from Inspection import Inspection
from Result import Result
from time import gmtime
import random
import numpy as np


class RandomNums(mongoengine.Document, base.SimpleDoc):
	# Not sure if we'll keep this, but gives us a bunch of random 
	# numbers stored in mongo
	
	_randNums = mongoengine.ListField()
	
	def rerand(self, numRand):
		# This is to construct a bunch of random numbers if they
		# aren't already in the DB
		
		self._randNums.append(random.random())
		for i in range(numRand - 1):
			self._randNums.append(self._randNums[-1] + (random.random() - .5))

	def save(self):
		self._randNums.append(self._randNums[-1] + (random.random() - .5))
		self._randNums.pop(0)
		super(RandomNums, self).save()
		

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
	
		
	def execute(self):
		# Get the resultset
		# Currently assume only one query (which will give random data)
		r = ResultSet()
		resultSet = r.execute(self.queryInfo)
		
		# Check if any descriptive processing
		if (self.descInfo):
			d = DescriptiveStatistic()
			resultSet = d.execute(resultSet, self.descInfo)
		
		# Create and return the chart
		c = Chart()
		chartSpec = c.createChart(resultSet, self.chartInfo)
		return chartSpec
	
	def setupRandomChart(self):
		self.name = 'Random'
		self.queryInfo = dict( name = 'Random' )
		self.descInfo = None
		self.chartInfo = dict ( name='Line', color = 'blue')
		
		
	def setupRandomMovingChart(self):
		self.name = 'RandomMoving'
		self.queryInfo = dict( name = 'Random' )
		self.descInfo = dict( formula = 'moving', window = 3)
		self.chartInfo = dict ( name='Line', color = 'blue')
		
		

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
		
		if (queryInfo['name'] == 'Random'):
			# Get our list of random numbers
			r = RandomNums.objects.first()
			
			# Hack to make sure there are random numbers in the DB
			if not r:
				r = RandomNums()
				r.rerand(20)
				
			r.save()
			
			# Column vector of sequence from 0 to the number of random elements
			xvals = np.array(range(len(r._randNums))).reshape(len(r._randNums),1)
			
			# Column vector from the random numbers
		 	yvals = np.array(r._randNums).reshape(len(r._randNums),1)
		 	
			randomValues = np.hstack((xvals, yvals)).tolist()
			
			dataset = { 'startTime': gmtime(),
					    'endTime': gmtime(),
					    'timestamp': gmtime(),
					    'labels': {'dim1': 'X-axis', 'dim2': 'Y-axis'},
					    'data': randomValues}
					   
			return dataset

		if (queryInfo['name'] == 'Motion'):
			insp = Inspection.objects.get(name='Motion')

			outputVals = [[r.capturetime, r.numeric] for r in Result.objects(inspection = insp.id)]
			
			dataset = { 'startTime': 'all',
					    'endTime': 'all',
					    'timestamp': gmtime(),
					    'labels': {'dim1': 'Time', 'dim2': 'Motion'},
					    'data': outputVals}
					   
			return dataset
