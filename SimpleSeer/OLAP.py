from base import *
from time import gmtime
import numpy as np


class OLAP:
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

	# Chart Options
	_chartType = 'line'
	_chartColor = 'blue'

	#def __init__(self):
		# Still need to what is passed to this constructor
		
		
	def createChart(self):
		# Currently assume just one query, just create default query string
		q = Query()
		queryString = q.createQuery('', '', '', gmtime(), gmtime())
		resultSet = q.execute(queryString)
		
		# No cube yet
		cubeSlice = resultSet
		
		# Create and return the chart
		c = Chart()
		return c.createChart(cubeSlice, self._chartType, self._chartColor)


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
			arrSize = 20
			# Column vector of sequence from 0 to arrSize
			xvals = np.array(range(arrSize)).reshape(arrSize,1)
			# Column vector of random numbers
		 	yvals = np.random.rand(1, arrSize)[0].reshape(arrSize,1)
			randomValues = np.hstack((xvals, yvals))
			
			dataset = { 'startTime': gmtime(),
					    'endTime': gmtime(),
					    'timestamp': gmtime(),
					    'labels': {'dim1': 'X-axis', 'dim2': 'Y-axis'},
					    'data': randomValues}
					   
			return dataset

	
	
