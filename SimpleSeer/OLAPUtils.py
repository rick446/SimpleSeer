from .models.OLAP import OLAP
from .models.Measurement import Measurement
from .models.Inspection import Inspection
from .models.Result import Result

import logging
log = logging.getLogger(__name__)


class OLAPFactory:
    
    def fromObject(self, obj):
        # Create an OLAP object from another query-able object
        
        # Find the type of object and 
        # get a result to do some guessing on the data types
        if type(obj) == Measurement:
            queryType = 'measurement'
            r = Result.objects(measurement = obj.id).limit(1)[0]
        elif type(obj) == Inspection:
            queryType = 'inspection'
            r = Result.objects(measurement = obj.id).limit(1)[0]
        else:
            log.warn('OLAP factory got unknown type %s' % str(type(obj)))
        
        
        # Setup the fields.  Begin by assuming always want capturetime and id's of measurement, inspection, frame
        fields = ['capturetime', 'measurement', 'inspection', 'frame']
        
        # If the string value is set, assume want to use it.  Otherwise, numeric
        if (r.string):
            fields.append('string')
        else:
            fields.append('numeric')
        
        # Put together the OLAP
        o = OLAP()
        o.name = obj.name
        o.queryType = queryType
        o.queryId = obj.id
        o.fields = fields
        
        # Fill in the rest with default values
        return self.fillOLAP(o)
        
    
    def fillOLAP(self, o):
        # Fills in default values for undefined fields of an OLAP
        
        # First, need to know how results are found
        if not o.queryType:
            o.queryType = 'measurement'
        
        # Get an object of that type for reference
        if o.queryType == 'measurement':
            objType = Measurement
        elif o.queryType == 'inspection':
            objType = Inspection

        # If a queryID specified, base everything off that object
        # Otherwise, base off the first object of that type
        if o.queryId:
            obj = objType.objects(id=o.queryId)
        else:
            obj = objType.objects[0]
            o.queryId = obj.id
        
        # Create a name based off the object's name and random number
        if not o.name:
            from random import randint
            o.name = obj.name + ' OF ' + str(randint(1, 1000000))
            
        # Default to max query length of 1000
        if not o.maxLen:
            o.maxLen = 1000
            
        # The standard set of fields per query
        if not o.fields:
            o.fields = ['capturetime', 'string', 'measurement', 'inspection', 'frame']
            
        # No mapping of output values
        if not o.valueMap:
            o.valueMap = {}
    
        # No since constratint
        if not o.since:
            o.since = None
        
        # No before constraint
        if not o.before:
            o.before = None
            
        # No custom filters
        if not o.customFilter:
            o.customFilter = {}
    
        # Finally, run once to see if need to aggregate
        if not o.statsInfo:
            results = o.execute()
            
            # If to long, do the aggregation
            if len(results) > o.maxLen:
                self.autoAggregate(results, autoUpdate=False)
            
        
        # Return the result
        # NOTE: This OLAP is not saved 
        return o
    


