from .models.Frame import Frame

class Filter():
	
	def getFrames(self):
		
		frs = [Frame.objects[0], Frame.objects[1], Frame.objects[2]]
		return 3, frs, Frame.objects[0].capturetime
	
	def checkFilter(self, filterType, filterName, filterFormat):
		from datetime import datetime
		
		if not filterFormat in ['numeric', 'string', 'autofill', 'datetime']:
			return {"error":"unknown format"}
		if not filterType in ['measurement', 'frame', 'framefeature']:
			return {"error":"unknown type"}
			
		db = Frame._get_db()
		
		pipeline = []
		collection = ''
		field = ''
		
		if filterType == 'frame':
			collection = 'frame'	
			field = filterName
		elif filterType == 'measurement':
			collection = 'result'
			field = filterFormat
			if (field == 'autofill'):
				field = 'string'
			
			pipeline.append({'$match': {'measurement_name': filterName}})
			
		elif filterType == 'framefeature':
			print filterName
			feat, c, field = filterName.partition('.')
			field = 'features.' + field
			collection = 'frame'
		
			pipeline.append({'$unwind': '$features'})
			pipeline.append({'$match': {'features.featuretype': feat}})
			
		if (filterFormat == 'numeric') or (filterFormat == 'datetime'):
			pipeline.append({'$group': {'_id': 1, 'min': {'$min': '$' + field}, 'max': {'$max': '$' + field}}})
		
		if (filterFormat == 'autofill'):
			pipeline.append({'$group': {'_id': 1, 'enum': {'$addToSet': '$' + field}}})	
			
		if (filterFormat == 'string'):
			pipeline.append({'$group': {'_id': 1, 'found': {'$sum': 1}}})
		
		cmd = db.command('aggregate', collection, pipeline = pipeline)
		
		ret = {}
		if len(cmd['result']) > 0:
			for key in cmd['result'][0]:
				if type(cmd['result'][0][key]) == list:
					cmd['result'][0][key].sort()
				
				if type(cmd['result'][0][key]) == datetime:
					cmd['result'][0][key] = int(float(cmd['result'][0][key].strftime('%s.%f')) * 1000)
				if not key == '_id':
					ret[key] = cmd['result'][0][key]
		else:
			return {"error":"no matches found"}
				
		return ret
		
		
	
	def getFilterOptions(self):
		
		return dict(self.frameFilterOptions().items() + self.measurementFilterOptions().items() + self.featureFilterOptions().items())
		
	def frameFilterOptions(self):
		from bson import Code
		db = Frame._get_db()
		
		frameOpts = {}
		
		pipeline = [{'$group': {'_id': 1, 'mintime': {'$min': '$capturetime'}, 'maxtime': {'$max': '$capturetime'}}}]
		cmd = db.command('aggregate', 'frame', pipeline = pipeline)
		
		c = cmd['result'][0]
		frameOpts['capturetime'] = {'type': 'datetime', 'min': int(float(c['mintime'].strftime('%s.%f')) * 1000), 'max': int(float(c['maxtime'].strftime('%s.%f')) * 1000)}
		
		metas = {}
		
		for f in Frame.objects:
			if f.metadata:
				for key in f.metadata:
					print 'checking for k: %s v: %d' % (key, val)
					if key in metas and not val in metas[key]:
						metas[key].append(val)
					else:
						metas[key] = [val]
		
		for key, val in metas.items():
			metas[key].sort()
			frameOpts[key] = {'type': 'enum', 'vals': metas[key]}
		
		
		return frameOpts
		
	def measurementFilterOptions(self):
		db = Frame._get_db()
		
		measOpts = {}
		
		pipeline = [{'$unwind': '$results'}, {'$group': {'_id': '$results.measurement_name', 'max': {'$max': '$results.numeric'}, 'min': {'$min': '$results.numeric'}}}]
		cmd = db.command('aggregate', 'frame', pipeline=pipeline)
		
		for m in cmd['result']:
			if m['_id']:
				if ('max' in m) and ('min' in m):
					measOpts[m['_id']] = {'type': 'numeric', 'min':m['min'], 'max':m['max']}
				else:
					measOpts[m['_id']] = {'type': 'string'}

		return measOpts

	def featureFilterOptions(self):
		db = Frame._get_db()
		
		featOpts = {}
		
		pipeline = [{'$unwind': '$features'}, {'$group': {'_id': '$features.featuretype',
		                                                  'minx': {'$min': '$features.x'},
		                                                  'maxx': {'$max': '$features.x'},
		                                                  'miny': {'$min': '$features.y'},
		                                                  'maxy': {'$max': '$features.y'},
		                                                  'minarea': {'$min': '$features.area'},
		                                                  'maxarea': {'$max': '$features.area'},
		                                                  'minwidth': {'$min': '$features.width'},
		                                                  'maxwidth': {'$max': '$features.width'},
		                                                  'minheight': {'$min': '$features.height'},
		                                                  'maxheight': {'$max': '$features.height'},
		                                                  'minangle': {'$min': '$features.angle'},
		                                                  'maxangle': {'$max': '$features.angle'},
		                                                  'meancolor': {'$min': '$features.meancolor'}} }]
		                                                  
		cmd = db.command('aggregate', 'frame', pipeline=pipeline)
		
		for f in cmd['result']:
			if f['_id']:
				if ('minx' in f) and ('maxx' in f):
					featOpts[f['_id'] + '.x'] = {'type': 'numeric', 'min': f['minx'], 'max': f['maxx']}
				if ('miny' in f) and ('maxy' in f):
					featOpts[f['_id'] + '.y'] = {'type': 'numeric', 'min': f['miny'], 'max': f['maxy']}
				if ('minarea' in f) and ('maxarea' in f):
					featOpts[f['_id'] + '.area'] = {'type': 'numeric', 'min': f['minarea'], 'max': f['maxarea']}
				if ('minwidth' in f) and ('maxwidth' in f):
					featOpts[f['_id'] + '.width'] = {'type': 'numeric', 'min': f['minwidth'], 'max': f['maxwidth']}
				if ('minheight' in f) and ('maxheight' in f):
					featOpts[f['_id'] + '.height'] = {'type': 'numeric', 'min': f['minheight'], 'max': f['maxheight']}
				if ('minangle' in f) and ('maxangle' in f):
					featOpts[f['_id'] + '.angle'] = {'type': 'numeric', 'min': f['minangle'], 'max': f['maxangle']}
				if 'meancolor' in f:
					featOpts[f['_id'] + '.meancolor'] = {'type': 'string'}

		return featOpts
