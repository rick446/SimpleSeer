import gc
from SimpleSeer import models as M
from SimpleSeer.Controls import Controls
import time
from gevent import sleep
import datetime
import bson
import SimpleSeer.realtime as realtime


#servo constants
fwheel_pos1 = 97
fwheel_pos2 = 163
fwheel_pos4 = 23
fwheel_pos5 = 0

rwheel_pos2 = 130
rwheel_pos3 = 157

SLEEPTIME = 1
aggtime = 15
ROTATE_TIME = 1
RATE=0.5

colors = ['purple', 'red', 'orange', 'yellow', 'green']

            
def servo_initialize(core):
    core.publish("ControlOutput/", { "fwheel": fwheel_pos2 })
    core.publish("ControlOutput/", { "rwheel": rwheel_pos3 })
    sleep(SLEEPTIME)

def servo_inspection(core):
    core.publish("ControlOutput/", { "fwheel": fwheel_pos1 })
    core.publish("ControlOutput/", { "rwheel": rwheel_pos3 })
    sleep(SLEEPTIME)

def servo_notgood(core):
    core.publish("ControlOutput/", { "rwheel": rwheel_pos2})
    core.publish("ControlOutput/", { "fwheel": fwheel_pos4 - 10 })
    sleep(0.1)
    
    core.publish("ControlOutput/", { "fwheel": fwheel_pos4 })
    sleep(SLEEPTIME)

def servo_good(core):
    core.publish("ControlOutput/", { "rwheel": rwheel_pos3 })
    core.publish("ControlOutput/", { "fwheel": fwheel_pos5 })
    sleep(0.2)
    core.publish("ControlOutput/", { "fwheel": fwheel_pos5 + 10})
    sleep(0.1)
    core.publish("ControlOutput/", { "fwheel": fwheel_pos5 })
    sleep(SLEEPTIME)
     

@core.state('start')
def start(state):
    core = state.core
    core.set_rate(10)
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
    servo_initialize(core)
    M.Alert.clear()
    for c in colors:
        core.publish("ControlOutput/", { c: False })
        
    while True:
        core.tick()
    
@core.on('waitforbutton', "ControlInput/")
def selectcolor(state, channel, message):
    core = state.core
    core.starttime = datetime.datetime.utcnow()
    core.matchcolor = message['color']
    core.publish("ControlOutput/", { message['color']: True })
    M.Alert.clear()
    M.Alert.info(message['color'] + " button pressed")

    return state.transition('inspect')
    
@core.state("getmarble")
def getmarble(state):
    servo_initialize(state.core)
    return state.core.state('inspect')

@core.state("inspect")
def inspect(state):
    core = state.core
    servo_inspection(core)
    core.inspecttime = datetime.datetime.utcnow()
    
    while True:
        gc.collect()
        core.capture()
        core.publish('capture/', { "capture": 1})

        core.inspect()

        r = core.results[-1][0] #NEED TO CHANGE THIS IF WE ADD NEW RESULTS
        f = core.lastframes[-1][0]

        if len(r):
          print "Result: ", r[0].string
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
            print jsonencode([r,r2])
            f.results.extend([r,r2])
            M.Alert.clear()
            M.Alert.info(res[0].string + " delivered")
            f.save(safe = False)
            return core.state("good")
          else:
            M.Alert.clear()
            M.Alert.info(res[0].string + " found, checking next item")
            f.save(safe = False)
            return core.state('notgood')
          
          
        else:
            since = (datetime.datetime.utcnow() - core.inspecttime).seconds
            if since > 1:
               return core.state('notgood')

@core.state("good")
def good(state):
    servo_good(state.core)
    return state.core.state("waitforbutton")
               
@core.state("notgood")
def notgood(state):
    servo_notgood(state.core)
    return state.core.state("getmarble")
    


