from base import *
from Session import Session
from time import gmtime
import random
import numpy as np


class RandomNums(SimpleDoc):
	# Not sure if we'll keep this, but gives us a bunch of random 
	# numbers stored in mongo
	
	_randNums = mongoengine.ListField()
	

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

	_name = mongoengine.StringField()
	_queryString = mongoengine.StringField()
	_queryTimeStamp = mongoengine.DateTimeField()
	_queryStartTime = mongoengine.DateTimeField()
	_queryEndTime = mongoengine.DateTimeField()
	_chartType = mongoengine.StringField()
	_chartColor = mongoengine.StringField()
	
		
	def createAll(self):
		# Get the resultset
		# Currently assume only one query (which will give random data)
		resultSet = self.createQuery()
		
		# No descriptives, cube, inferrential yet
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

	
#class DescriptiveStatistic:
	# Will be used for computing basic descriptives on query results
	# (e.g., sums, counts, means, moving averages)
	

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

	
	
