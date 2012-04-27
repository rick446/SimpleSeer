from base import *
from Session import Session
from time import gmtime
import random
import numpy as np


class RandomNums(SimpleDoc):
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
		

class OLAP(SimpleDoc):
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

	olapName = mongoengine.StringField()
	_queryString = mongoengine.StringField()
	_descriptive = mongoengine.StringField()
	_queryTimeStamp = mongoengine.DateTimeField()
	_queryStartTime = mongoengine.DateTimeField()
	_queryEndTime = mongoengine.DateTimeField()
	_chartType = mongoengine.StringField()
	_chartColor = mongoengine.StringField()
	
		
	def createAll(self):
		# Get the resultset
		# Currently assume only one query (which will give random data)
		resultSet = self.createQuery()
		
		if (self._descriptive):
			d = DescriptiveStatistic()
			resultSet = d.execute(resultSet)
		
		# No cube, inferrential yet
		cubeSlice = resultSet
		
		# Create and return the chart
		# Right now, just set some default values
		_chartType = 'line'
		_chartColor = 'blue'
		return self.createChart(cubeSlice)


	def createQuery(self):
		# Currently assume just one query, just create default query string
		q = Query()
		self._queryString = q.createQuery('', '', '', self._queryStartTime, self._queryEndTime)
		resultSet = q.execute(self._queryString)		
		return resultSet
		
		
	def createChart(self, slice, chartType = '', chartColor = ''):
		# Check if need to update the chart spec
		if chartType: self._chartType = chartType
		if chartColor: self._chartColor = chartColor
		
		# Generate and return the chart
		c = Chart()
		chartSpec = c.createChart(slice, self._chartType, self._chartColor)
		return chartSpec
		
	def installRandomOLAP(self):
		newRand = OLAP()
		newRand.olapName = 'Random'
		newRand._queryString = 'random'
		newRand._chartType = 'line'
		newRand._chartColor = 'green'
		newRand.save()
		
	def installRandomMovingOLAP(self):
		newMove = OLAP()
		newMove.olapName = 'RandomMoving'
		newMove._queryString = 'random'
		newMove._descriptive = 'moving'
		newMove._chartType = 'line'
		newMove._chartColor = 'green'
		newMove.save()
		

class Chart:
	# Takes the data and puts it in a format for charting
	
	def createChart(self, slice, chartType='line', chartColor='blue'):
		# This function will change to handle the different formats
		# required for different charts.  For now, just assume nice
		# graphs of (x,y) coordiantes
		
		chartData = { 'chartType': chartType,
					  'chartColor': chartColor,
					  'labels': slice['labels'],
					  'data': slice['data'].tolist() }
		
		return chartData
					  
#class Cube:
	# Will eventually be used to hold the data from various queries,
	# merging them together, in preparation for eventual slicing and
	# dicing, data anlysis, and other charting

	
class DescriptiveStatistic:
	# Will be used for computing basic descriptives on query results
	# (e.g., sums, counts, means, moving averages)

	# TODO: This is just a quick hack to make it work.  Future: make
	# more plugin-able and configurable
	
	def execute(self, resultSet, statisticName = 'moving'):
		if statisticName == 'moving':
			window = 5 # moving average over last 5 entries
			
			# assume I want to do the averge on the second dimension
			xvals, yvals = np.hsplit(resultSet['data'], 2)
			weights = np.repeat(1.0, window) / window
			yvals = np.convolve(yvals.flatten(), weights)[window-1:-(window-1)]
			print yvals
			xvals = xvals[window-1:]
			
			resultSet['data'] = np.hstack((xvals, yvals.reshape(len(xvals),1)))
			return resultSet

#class InferentialStatistic:
	# Will do post- processing of the data, to examine how one variable 
	# is related to another	

class Query:	
	# Class to retrieve data from the database and return as
	# Numpy matrix
	
	
	def createQuery(self, objects, filters, groupBy, startTime, endTime):
		# Take user input from web forms and convert into query
		# for MongoDB
		#
		# TODO: Still to be implemented, pending development of VQL
		# For now, just return random for a random query string
		
		return 'random'
	
	
	def execute(self, queryString):
		# Execute the querystring, returning the results of the
		# query as a numpy vector
		#
		# Entering a 'random' querystring will return a matrix with
		# sequential x values and random y values between 0 and 1
		#
		# TODO: Still to be fully implemented, pending development of
		# VQL.  
		
		if (queryString == 'random'):
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
		 	
			randomValues = np.hstack((xvals, yvals))
			
			dataset = { 'startTime': gmtime(),
					    'endTime': gmtime(),
					    'timestamp': gmtime(),
					    'labels': {'dim1': 'X-axis', 'dim2': 'Y-axis'},
					    'data': randomValues}
					   
			return dataset

	
	
