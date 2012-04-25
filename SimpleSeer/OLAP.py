from time import gmtime
import numpy as np
import json

	
class Query:	
	
	def execute(self, queryString):
		
		if (queryString == 'random'):
			arrSize = 5
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

	
	
class Chart:

	def createChart(self, slice):
		chartData = { 'chartType': 'line',
					  'color': 'blue',
					  'labels': slice['labels'],
					  'data': slice['data'].tolist() }
		
		return chartData
					  
