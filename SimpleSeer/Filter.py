from .models.Frame import Frame
from datetime import datetime

class Filter():
	
	def getFrames(self, allFilters, skip=0, limit=0):
		
		pipeline = []
		frames = []
		measurements = []
		features = []
		
		for f in allFilters:
			if f['type'] == 'measurement':
				measurements.append(f)
			elif f['type'] == 'frame':
				frames.append(f)
			elif f['type'] == 'framefeature':
				features.append(f)
		
		if frames:
			for f in frames:
				
				if 'eq' in f:
					if f['name'] == 'capturetime':
						f['eq'] = datetime.fromtimestamp(f['eq'] / 1000)
					comp = f['eq']
				else:
					comp = {}
					if 'gt' in f and f['gt']:
						if f['name'] == 'capturetime':
							f['gt'] = datetime.fromtimestamp(f['gt'] / 1000)
						comp['$gt'] = f['gt']
					if 'lt' in f and f['lt']:
						if f['name'] == 'capturetime':
							f['lt'] = datetime.fromtimestamp(f['lt'] / 1000)
						comp['$lt'] = f['lt']
				
				pipeline.append({'$match': {f['name']: comp}})
		
		if measurements:
			proj = {'ok': self.condMeas(measurements)}
			group = {'allok': {'$min': '$ok'}}
			
			
			for key in Frame._fields:
				if key == 'id':
					key = '_id'
				proj[key] = 1
				group[key] = {'$first': '$' + key}
			
			group['_id'] = '$_id'
		
			
			pipeline.append({'$unwind': '$results'})
			pipeline.append({'$project': proj})
			pipeline.append({'$group': group})
			pipeline.append({'$match': {'allok': 1}})
			
		if features:
			proj = {'ok': self.condFeat(features)}
			group = {'allok': {'$min': '$ok'}}
			
			
			for key in Frame._fields:
				if key == 'id':
					key = '_id'
				proj[key] = 1
				group[key] = {'$first': '$' + key}
			
			group['_id'] = '$_id'
		
			
			pipeline.append({'$unwind': '$features'})
			pipeline.append({'$project': proj})
			pipeline.append({'$group': group})
			pipeline.append({'$match': {'fails': 0}})
			
			
			
		pipeline.append({'$sort': {'capturetime': 1}})
		
		print pipeline
				
		db = Frame._get_db()
		cmd = db.command('aggregate', 'frame', pipeline = pipeline)
		
		ids = []
		for r in cmd['result']:
			ids.append(r['_id'])
	
		if skip < len(ids):
			if (skip + limit) > len(ids):
				ids = ids[skip:]
			else:
				ids = ids[skip:skip+limit]
		else:
			return 0, None, datetime(1970, 1, 1)
		
		frames = Frame.objects.filter(id__in=ids)
        
		frs = []
		for f in frames:
			frs.append(f)
		
		if len(frs) > 0:
			earliest = frs[0].capturetime
		else:
			earliest = datetime(1970, 1, 1)
		
		
		return len(cmd['result']), frs, earliest
		
	
	def condMeas(self, measurements):
		
		# Basic output should look like:
		# (NOT name match) OR (values match)
		# So that always passes if does not match this result
		# Or will pass if the values match the query
		
		allfilts = []
		for m in measurements:	
			
			if 'eq' in m:
				comp = {'$eq': ['$results.string', str(m['eq'])]}
			else:
				tmp = []
				if 'gt' in m:
					tmp.append({'$gte': ['$results.numeric', m['gt']]})
				if 'lt' in m:
					tmp.append({'$lte': ['$results.numeric', m['lt']]})	
				
				if len(tmp) > 1:
					comp = {'$and': tmp}
				else:
					comp = tmp[0]
			
			name = {'$not': [{'$eq': ['$results.measurement_name', str(m['name'])]}]}
			combined = {'$or': [name, comp]}
			allfilts.append(combined)
				
		return {'$cond': [{'$and': allfilts}, 1, 0]}
		
		
	def condFeat(self, features):
		
		allfilts = []
		for f in features:
			feat, c, field = f['name'].partition('.')
			
			if 'eq' in f:
				comp = {'$eq': ['$features.' + field, f['eq']]}
			else:
				temp = []
				if 'gt' in f:
					tmp.append({'$gte': ['$features.' + field, f['gt']]})
				if 'lt' in f:
					tmp.append({'$lte': ['$features.' + field, f['lt']]})
					
			if len(tmp) > 1:
				comp = {'$and': tmp}
			else:
				comp = tmp[0]
			
			name = {'$not': [{'$eq': ['$features.featuretype', str(m['name'])]}]}
			combined = {'$or': [name, comp]}
			allfilts.append(combined)
			
		return {'$cond': [{'$and': allfilts}, 1, 0]}
		
		
		
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
