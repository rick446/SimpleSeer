from .models.Result import Result

class Filter():
	
	def getFilterOptions(self):
		opts = {}
		
		rmin = Result.objects[0]
		rmax = Result.objects[len(Result.objects) - 1]
		
		opts['capturetime'] = {'type': 'datetime', 'min':int(float(rmin['capturetime'].strftime('%s.%f')) * 1000), 'max':int(float(rmax['capturetime'].strftime('%s.%f')) * 1000)}
		opts['deliverytime'] = {'type': 'numeric', 'min':1000, 'max':1200}
		opts['partname'] = {'type': 'enum', 'vals': ['F1001', 'QX3000', 'ABC123']}
		opts['color'] = {'type': 'string'}
		
		return opts
		
		
