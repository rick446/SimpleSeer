from .models.OLAP import OLAP
from .models.Measurement import Measurement
from .models.Inspection import Inspection
from .models.Result import Result

from gevent import Greenlet, sleep
from datetime import datetime, timedelta
from time import mktime

from .util import utf8convert
from .realtime import ChannelManager

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
    


class RealtimeOLAP():
    
    def realtime(self, res):

    
        from .models.Chart import Chart
        
        olaps = OLAP.objects(__raw__={'$or': [ {'queryType': 'measurement_id', 'queryId': res.measurement_id}, 
                                               {'queryType':'inspection_id', 'queryId': res.inspection_id}
                                             ]}) 
        
        for o in olaps:
            # If no statistics, just send result on its way
            if not o.statsInfo:
                data = self.resToData(o, res)
                
                
                if len(data) > 0:
                    # Long term fix: only publish to charts that are listened to
                    cs = Chart.objects(olap = o.name)
                    
                    for c in cs:
                        chartData = c.mapData([data])
                        self.sendMessage(o, chartData)
    
    def resToData(self, o, res):
        
        # Have to enforce: filter
        results = {}
        
        sinceok = (not o.since) or (res.capturetime > o.since)
        beforeok = (not o.before) or (res.capturetime < o.before)
        if not o.customFilter:
            filterok = True
        else:
            key, val = o.customFilter.items()[0]
            if res.__getattribute__(key) == val:
                filterok = True
            else:
                filterOK = False
        
        if sinceok and beforeok and filterok:
            
            # Use only the specified fields
            for f in o.fields:
                results[f] = res.__getattribute__(f) 
                
                # Map the values, if applicable
                if (o.valueMap) and (o.valueMap['field'] == f):
                    results[f] = o.valueMap.get(f, default = o.valueMap['default']) 
        
        return results

    def sendMessage(self, o, data):
        if (len(data) > 0):
            msgdata = dict(
                olap = str(o.name),
                data = data)
            
            olapName = 'OLAP/' + utf8convert(o.name) + '/'
            ChannelManager().publish(olapName, dict(u='data', m=msgdata))
            

class ScheduledOLAP():
    
    def runSked(self):
        
        log.info('Starting statistics schedules')
        
        glets = []
        
        glets.append(Greenlet(self.skedLoop, 'minute'))
        glets.append(Greenlet(self.skedLoop, 'hour'))
        glets.append(Greenlet(self.skedLoop, 'day'))
    
        # Start all the greenlets
        for g in glets:
            g.start()
            
        # Join all the greenlets
        for g in glets:
            g.join()
        
        
    def skedLoop(self, interval):
        
        from datetime import datetime
        
        nextTime = datetime.utcnow()
        
        while (True):
            log.info('Checking for OLAPs running every %s' % interval)
            
            # Split the time into components to make it easier to round
            year = nextTime.year
            month = nextTime.month
            day = nextTime.day
            hour = nextTime.hour
            minute = nextTime.minute
            
            # Setup the start and end time for the intervals
            if interval == 'minute':
                endBlock = datetime(year, month, day, hour, minute)
                startBlock = endBlock - timedelta(0, 60)
                nextTime = endBlock + timedelta(0, 61)
                sleepTime = 60
            elif interval == 'hour':
                endBlock = datetime(year, month, day, hour, 0)
                startBlock = endBlock - timedelta(0, 3600)
                nextTime = endBlock + timedelta(0, 3661)
                sleepTime = 3600
            elif interval == 'day':
                endBlock = datetime(year, month, day, 0, 0)
                startBlock = endBlock - timedelta(1, 0)
                nextTime = endBlock + timedelta(1, 1)
                sleepTime = 86400
            
            # OLAPs assume time in epoch seconds
            startBlockEpoch = mktime(startBlock.timetuple())
            endBlockEpoch = mktime(endBlock.timetuple())

            # Find all OLAPs that run on this time interval
            os = OLAP.objects(groupTime = interval) 
    
            # Have each OLAP send the message
            for o in os:
                
                log.info('%s running per %s' % (o.name, interval)) 
                
                o.since = startBlockEpoch
                o.before = endBlockEpoch
                data = o.execute()
                
                # Cheat and use the realtime's send message function
                ro = RealtimeOLAP()
                ro.sendMessage(o, data)
            
            # Set the beginning time interval for the next iteraction
            sleepTime = (nextTime - datetime.utcnow()).total_seconds()
            
            # Wait until time to update again
            sleep(sleepTime)
