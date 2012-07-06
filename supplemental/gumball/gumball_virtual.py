import gc
from SimpleSeer import models as M
#from SimpleSeer.Controls import Controls
import time
from gevent import sleep
import datetime
import bson
import SimpleSeer.realtime as realtime
from random import random, randint

import logging


RATE=0.5
colors = ['purple', 'red', 'orange', 'yellow', 'green']

BUTTON_PAUSE = 15
MARBLE_PAUSE = 5
            
log = logging.getLogger(__name__)     

@core.state('start')
def start(state):
    core = state.core
    core.set_rate(RATE)
    core.colormatch_measurement = M.Measurement.objects(method="closestcolor")[0]
    core.timesince_measurement = M.Measurement.objects(method="timebetween_manual")[0]
    core.deliveredcolor_measurement = M.Measurement.objects(method="closestcolor_manual")[0]
    core.region_inspection = M.Inspection.objects[0]
    core.capture()
    core.publish('capture/', { "capture": 1})
    
    return core.state('waitforbutton')
    

@core.state('waitforbutton')
def waitforbutton(state):
    core = state.core
    
    time.sleep(random() * BUTTON_PAUSE)
    core.starttime = datetime.datetime.utcnow()
    
    log.info('Waiting for button')
    core.matchcolor = colors[randint(0, 4)]
    
    log.info('Looking for %s.' % core.matchcolor)
    
    return state.core.state('inspect')
    
    
@core.state("inspect")
def inspect(state):
    core = state.core
    core.inspecttime = datetime.datetime.utcnow()
    
    while True:
        gc.collect()
        core.capture()
        core.publish('capture/', { "capture": 1})

        core.inspect()

        r = core.results[-1][0] #NEED TO CHANGE THIS IF WE ADD NEW RESULTS
        f = core.lastframes[-1][0]

        if len(r):
          log.info('Found: %s' % r[0].string)
          res = r
          if (r[0].string == core.matchcolor):
            td = (datetime.datetime.utcnow() - core.starttime)
            timesince = float(td.seconds) + td.microseconds / 1000000.0
            
            r2 = M.ResultEmbed(
              result_id = bson.ObjectId(),
              measurement_id = core.deliveredcolor_measurement.id,
              measurement_name = core.deliveredcolor_measurement.name,
              inspection_id = core.region_inspection.id,
              inspection_name = core.region_inspection.name,
              numeric = None,
              string = str(core.matchcolor)
            )
            
            r = M.ResultEmbed(
              result_id = bson.ObjectId(),
              measurement_id = core.timesince_measurement.id,
              measurement_name = core.timesince_measurement.name,
              inspection_id = core.region_inspection.id,
              inspection_name = core.region_inspection.name,
              numeric = timesince,
              string = str(timesince)
            )
            from SimpleSeer.util import jsonencode
            f.results.extend([r,r2])
            f.save(safe = False)
            return core.state("good")
          else:
            f.save(safe = False)
            return core.state('notgood')
          
          
        else:
            since = (datetime.datetime.utcnow() - core.inspecttime).seconds
            if since > 1:
               return core.state('notgood')

@core.state("good")
def good(state):
    return state.core.state("waitforbutton")
               
@core.state("notgood")
def notgood(state):
    from random import random
    time.sleep(random()*MARBLE_PAUSE)
    return state.core.state("inspect")
    


