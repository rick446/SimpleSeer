from .models.Frame import Frame
from .models.Inspection import Inspection
from datetime import datetime

FIELD_NAMES = ['camera', 'capturetime', 'height', 'width']

class Filter():
	
	def getFrames(self, allFilters, skip=0, limit=0, sortinfo = {}, dictOutput=False):
		
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
		
		# TODO: We could add a lot more features here to optimization
		#pipeline.append({'$project': {'features.featurepickle_b64': 0}})
		
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
			proj, group = self.frameFields()
		
			proj['measok'] = self.condMeas(measurements)
			group['allmeasok'] = {'$sum': '$measok'}
			
			pipeline.append({'$unwind': '$results'})
			pipeline.append({'$project': proj})
			pipeline.append({'$group': group})
			pipeline.append({'$match': {'allmeasok': len(measurements)}})
		
		# Handle features	
		if features:
			proj, group = self.frameFields()
		
			proj['featok'] = self.condFeat(features)
			group['allfeatok'] = {'$sum': '$featok'}
			
			pipeline.append({'$unwind': '$features'})
			pipeline.append({'$project': proj})
			pipeline.append({'$group': group})
			pipeline.append({'$match': {'allfeatok': len(features)}})
			
		
		# Sort
		# TODO: some more fancy queries could pull just the relevant result/feature out for sorting
		if sortinfo:
			sortinfo['order'] = int(sortinfo['order'])
			if sortinfo['type'] == 'measurement':
				pipeline.append({'$sort': {'results.numeric': sortinfo['order'], 'results.string': sortinfo['order']}})
			elif sortinfo['type'] == 'framefeature':
				feat, c, field = sortinfo['name'].partition('.')
				pipeline.append({'$sort': {'features.' + field: sortinfo['order']}})
			else:
				print 'GOOD'
				pipeline.append({'$sort': {sortinfo['name']: sortinfo['order']}})
		
		print pipeline
		
		db = Frame._get_db()
		cmd = db.command('aggregate', 'frame', pipeline = pipeline)
		results = cmd['result']
		
		# Perform the skip/limit 
		# Note doing this in python instead of mongo since need original query to give total count of relevant results
		if skip < len(results):
			if (skip + limit) > len(results):
				results = results[skip:]
			else:
				results = results[skip:skip+limit]
		else:
			return 0, None
		
		#print results
		
		# Check if need to output as dict or as Frames
		if dictOutput:
			return len(cmd['result']), results	
		else:
			# Lookup the Frame objects by the ID frm the dict
			frs = [Frame.objects(id=r['_id'])[0] for r in results]
			return len(cmd['result']), frs
		
	
	def frameFields(self):
		proj = {}
		group = {}
		
		for key in Frame._fields:
			if key == 'id':
				key = '_id'
			proj[key] = 1
			
			if (key == 'results') or (key == 'frames'):
				group[key] = {'$push': '$' + key}
			else:
				group[key] = {'$first': '$' + key}
			
		group['_id'] = '$_id'

		return proj, group
	
	def condMeas(self, measurements):
		
		allfilts = []
		for m in measurements:	
			
			comp = []
			if 'eq' in m:
				comp.append({'$eq': ['$results.string', str(m['eq'])]})
			
			if 'gt' in m:
				comp.append({'$gte': ['$results.numeric', m['gt']]})
			
			if 'lt' in m:
				comp.append({'$lte': ['$results.numeric', m['lt']]})	
				
			comp.append({'$eq': ['$results.measurement_name', str(m['name'])]})
			combined = {'$and': comp}
			allfilts.append(combined)
				
		return {'$cond': [{'$or': allfilts}, 1, 0]}
		
		
	def condFeat(self, features):
		
		allfilts = []
		for f in features:
			feat, c, field = f['name'].partition('.')
			
			comp = []
			if 'eq' in f:
				comp.append({'$eq': ['$features.' + field, str(f['eq'])]})
			if 'gt' in f:
				comp.append({'$gte': ['$features.' + field, f['gt']]})
			if 'lt' in f:
				comp.append({'$lte': ['$features.' + field, f['lt']]})
					
			comp.append({'$eq': ['$features.featuretype', str(feat)]})
			combined = {'$and': comp}
			allfilts.append(combined)
			
		return {'$cond': [{'$or': allfilts}, 1, 0]}
		
		
		
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
		
	
	def toCSV(self, frames):
		import StringIO
		import csv
		
		# csv libs assume saving to a file handle
		f = StringIO.StringIO()
		
		frames = self.flattenFeature(frames)
		
		if len(frames) > 0:
			keys = frames[0].keys()
		
		# Convert the dict to csv
		csvDict = csv.DictWriter(f, keys)
		csvDict.writeheader()
		csvDict.writerows(frames)
		
		# Grab the string version of the output
		output = f.getvalue()
		f.close()
		
		return output
		
	def toExcel(self, frames):
		import StringIO
		from xlwt import Workbook, XFStyle
		
		# Need a file handle to save to
		f = StringIO.StringIO()
		
		frames = self.flattenFeature(frames)
		
		if len(frames) > 0:
			keys = frames[0].keys()
		
		# Construct a workbook with one sheet
		wb = Workbook()
		s = wb.add_sheet('frames')
		
		# Create the style for date/time
		dateStyle = XFStyle()
		dateStyle.num_format_str = 'MM/DD/YYYY HH:MM:SS'
		
		# Add the header/field labels
		r = s.row(0)
		for i, name in enumerate(keys):
			r.write(i, name)
		
		# Write the data
		for i, frame in enumerate(frames):
			print type(frame['capturetime'])
			for j, name in enumerate(keys):
				if type(frame[name]) == datetime:
					s.write(i+1, j, frame[name], dateStyle)
				else:
					s.write(i+1, j, str(frame[name]))
		
		# Save the the string IO and grab the string data
		wb.save(f)
		output = f.getvalue()
		f.close()
		
		return output
		
	def flattenFeature(self, frames):
		import pkg_resources
		
		# First pass is to find all possible feature names
		featkeys = {}
		
		for frame in frames:	
			for feature in frame['features']:
				# Don't check this feature type if already done
				if feature['featuretype'] not in featkeys:
					# Get to the plugin via the inspection
					# TODO: see if there is an easier way
					insp = Inspection.objects(id=feature['inspection'])[0]
					insp.register_plugins('seer.plugins.inspection')
					plugin = insp.get_plugin(insp.method)
					if 'printFields' in dir(plugin):
						featkeys[feature['featuretype']] = plugin.printFields()
					
				
		flatFrames = []
		# Second pass, construct the flattened list of dicts
		for frame in frames:
			tmpFrame = {}
			
			for key in FIELD_NAMES:
				tmpFrame[key] = frame[key]
			
			for featkey in featkeys.keys():
				thisFeat = {}
				for feat in frame['features']:
					if feat['featuretype'] == featkey:
						thisFeat = feat
				
				for k in featkeys[featkey]:
					tmpFrame[featkey + '.' + k] = thisFeat.get(k, 'N/A')
			
			flatFrames.append(tmpFrame)
			
		return flatFrames
