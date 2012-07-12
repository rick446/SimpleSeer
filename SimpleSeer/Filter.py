from .models.Result import Result
from .models.Measurement import Measurement
from .models.FrameFeature import FrameFeature

class Filter():
	
	def getFilterOptions(self):
		
		return dict(self.measurementFilterOptions().items() + self.featureFilterOptions().items())
		
	def measurementFilterOptions(self):
		db = Measurement._get_db()
		
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
		db = Measurement._get_db()
		
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
