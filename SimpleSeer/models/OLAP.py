import logging

import mongoengine
from .base import SimpleDoc

from formencode import validators as fev
from formencode import schema as fes
from SimpleSeer import validators as V
import formencode as fe

from datetime import datetime


log = logging.getLogger(__name__)


#################################
# name: Name of the OLAP object
# maxLen: Maximum numer of results to return, aggregate if number exceeds limit
# queryType: type of query: measurement or inspection.  e.g., 'measurement'
# queryId: the id of the object as referenced in previous step.  e.g., ObjectId('4fdbac481d41c834fb000001')
# fields: a list of fields to be returned.  e.g., ['capturetime', 'numeric', 'measurement']
# groupTime: time groupby interval: minute, hour, day
# valueMap: used to map output values to other values.  dict where the key is substituted with the value.  e.g., {'red': 3} will look for red and replace with 3.
#               must include 'field': the name of the field to map, e.g., {'field': 'string'}
#               must include 'default': the value when no other entry in the map works
#               rest of fieds are key/val pairs for the substitution
# since: limit to results where capturetime greater than time specified.  Time in epoch seconds
# before: limit to results where capturetime less than time specified.  Time in epoch seconds
# customFilter: dict of additional filter values.  e.g., {'string': 'yellow'}
# groupTime: used for aggreagating result.  Possible values are: minute, hour, day
# statsInfo: Select how to group and aggregate data.  List of dicts.  In each dict, the key is the name of the function and the val is the name of the field on which to apply the function
#       Possible functions based on mongo aggregation framework, such as first, last, max, min, avg, sum
# postProc: Stats function that require global data set (don't work well with mongo)
#       Possible functions: movingCount
#################################

  
class OLAPSchema(fes.Schema):
    name = fev.UnicodeString()            
    maxLen = fev.Int()
    queryType = fev.UnicodeString()
    queryId = fev.UnicodeString()
    #fields = V.JSON(if_empty=dict, if_missing=None)
    #valueMap = V.JSON(if_empty=dict, if_missing=None)
    groupTime = fev.UnicodeString()
    since = fev.Int()
    before = fev.Int()
    #customFilter = V.JSON(if_empty=dict, if_missing=None)   
    #statsInfo = V.JSON(if_empty=dict, if_missing=None)
    #postProc = V.JSON(if_empty=dict, if_missing=None)
    notNull = fev.Bool()

class OLAP(SimpleDoc, mongoengine.Document):

    name = mongoengine.StringField()
    maxLen = mongoengine.IntField()
    queryType = mongoengine.StringField()
    queryId = mongoengine.ObjectIdField()
    fields = mongoengine.ListField()
    groupTime = mongoengine.StringField()
    valueMap = mongoengine.DictField()
    since = mongoengine.IntField()
    before = mongoengine.IntField()
    customFilter = mongoengine.DictField()
    statsInfo = mongoengine.ListField()
    postProc = mongoengine.DictField()
    notNull = mongoengine.BooleanField()
    
    meta = {
        'indexes': ['name']
    }


    def __repr__(self):
        return "<OLAP %s>" % self.name

    def execute(self):
        
        results = self.doQuery()
        
        if len(results) > self.maxLen:
            results = self.autoAggregate(results)
        
        results = self.doPostProc(results)
        
        if (results == []) and (self.notNull):
            results = self.defaultOLAP()
        
        return results


    def doPostProc(self, results, realtime=False):
        
        if 'movingCount' in self.postProc:
            if realtime:
                full_res = self.doQuery()
                results[self.postProc['movingCount']] = len(full_res) + 1
                
            else:
                for counter, r in enumerate(results):
                    r[self.postProc['movingCount']] = counter + 1

        return results


    def doQuery(self):
        db = self._get_db()
        
        match = self.createMatch()
        project = self.createFields()
        stats = self.createStats()
        
        sort = {'capturetime': 1}
  
        pipeline = self.assemblePipeline(match, project, stats, sort)
  
        cmd = db.command('aggregate', 'result', pipeline=pipeline)
        return cmd['result']


    def assemblePipeline(self, match, project, stats, sort):
        
        pipeline = []
        
        # Will always have search criteria
        # But should eventually add handling to fail gracefully if not
        pipeline.append({'$match': match})
        
        # Will also have fields selected
        # But should eventually add handling to fail gracefully if not
        pipeline.append({'$project': project})
        
        # Always sort results by capturetime (not sure if this will ever be conditional)
        pipeline.append({'$sort': sort})
        
        # Handle stats, if they exist
        if stats:
            # First, the basic grouping/stats
            pipeline.append({'$group': stats})
            
            # Stats groups on _id field, which is inconsistent with non-grouped format
            # Use project to rename the _id field back to capturetime
            statsProject = {}
            
            for key, val in stats.iteritems():
                if key == '_id':
                    statsProject['capturetime'] = '$_id'
                    statsProject['_id'] = 0
                else:
                    statsProject[key] = 1
            
            pipeline.append({'$project': statsProject})
            
            # Operation messes up previous sorting, so re-sort
            pipeline.append({'$sort': sort})
        
        
        return pipeline


    def createMatch(self):
        
        match = {}

        # Filter to the relevant inspection/measurement
        match[self.queryType] = self.queryId
        
        # Time filters, since and before
        captureTime = {}
        if self.since:
            sinceTime = datetime.fromtimestamp(self.since)
            captureTime['$gte'] = sinceTime
        
        if self.before:
            beforeTime = datetime.fromtimestamp(self.before)
            captureTime['$lt'] = beforeTime
            
        if len(captureTime) > 0:
            match['capturetime'] = captureTime
        
        # Allow a custom filter field from the OLAP
        # TODO: Allow more than one filter
        if self.customFilter:
            filt = self.customFilter
            match[filt['field']] = filt['val']
            
        return match
            
    def createFields(self):
        # Select/construct the fields necessary
        fields = {}
        
        # First select the fields from Result to include
        for p in self.fields:
            fields[p] = 1
            
        
        # Construct a custom time field if need to group by time        
        if self.groupTime:
            if self.groupTime == 'minute':
                fields['t'] = { '$isoDate': { 'year': { '$year': '$capturetime' }, 
                                    'month': { '$month': '$capturetime' }, 
                                    'dayOfMonth': { '$dayOfMonth': '$capturetime' }, 
                                    'hour': { '$hour': '$capturetime' },
                                    'minute': { '$minute': '$capturetime'}}}
            elif self.groupTime == 'hour':
                fields['t'] = { '$isoDate': { 'year': { '$year': '$capturetime' }, 
                                    'month': { '$month': '$capturetime' }, 
                                    'dayOfMonth': { '$dayOfMonth': '$capturetime' }, 
                                    'hour': { '$hour': '$capturetime' }}}
            elif self.groupTime == 'day':
                fields['t'] = { '$isoDate': { 'year': { '$year': '$capturetime' }, 
                                    'month': { '$month': '$capturetime' }, 
                                    'dayOfMonth': { '$dayOfMonth': '$capturetime' }}}
 
        if self.valueMap:
            mapField = self.valueMap['field'] 
            fields[mapField] = self.createMap(self.valueMap)
    
        return fields
    
    def createStats(self):
        
        stats = {}
        
        
        if len(self.statsInfo) > 0:
            stats['_id'] = '$t'
            
            for s in self.statsInfo:
                key, val = s.items()[0]
                # Needs special handling for count
                if type(val) == int:
                    stats['count'] = {'$' + str(key): '$' + str(val)}
                else:
                    stats[str(val)] = {'$' + str(key): '$' + str(val)}
            
            
            return stats

    def createMap(self, mapInfo):
        
        thisMap = mapInfo.copy()
        
        # Grab the name of the field
        fieldName = '$' + thisMap.pop('field')
        
        # Grab the 'else' term
        defaultVal = thisMap.pop('default')
        
        
        return self.recurseMap(fieldName, defaultVal, thisMap)
    
    def recurseMap(self, fieldName, defaultVal, remainTerms):
        
        if len(remainTerms) > 0:
            key, val = remainTerms.popitem()            
            return {'$cond': [{'$eq': [fieldName, key]}, val, self.recurseMap(fieldName, defaultVal, remainTerms)]}
        else:
            return defaultVal

    def autoAggregate(self, resultSet, autoUpdate = True):
        oldest = resultSet[-1]
        newest = resultSet[0]
        
        elapsedTime = (newest['capturetime'] - oldest['capturetime']).total_seconds()
        timeRange = elapsedTime / self.maxLen
            
        # Set the grouping interval
        if timeRange < 60: self.groupTime = 'minute'
        elif timeRange < 3600: self.groupTime = 'hour'
        else: self.groupTime = 'day'

        # Decide how to group
        # If already grouped (has stats info), don't change it
        if len(self.statsInfo) == 0:
            # For string items, use the last element in the group
            # For numeric items, take the average
            for key, val in oldest.iteritems():
                
                if not key == '_id':
                    if (type(val) == int) or (type(val) == float):
                        self.statsInfo.append({'avg': key})
                    else:
                        self.statsInfo.append({'first': key})
        
        if autoUpdate:
            self.save()
            return self.doQuery()
        
        else:
            return []

    def defaultOLAP(self):
        from bson import ObjectId
        # Returns data set of all default values, formatted for this olap
        
        fakeResult = {}
        
        for f in self.fields:
            if f == self.queryType:
                fakeResult[f] = self.queryId
            elif f[-2:] == 'id':
                fakeResult[f] = ObjectId()
            elif f == 'capturetime':
                fakeResult[f] = datetime(1970, 1, 1)
            elif f == 'string':
                fakeResult[f] = '0'
            elif f == 'numeric':
                fakeResult[f] = 0
            else:
                fakeResult[f] = 0
                
        fakeResult['_id'] = ObjectId()
                
        return [fakeResult]
