import gc
from SimpleSeer import models as M
from SimpleSeer.Controls import Controls
import time
import datetime
import bson
import SimpleSeer.realtime as realtime


RATE=0.5

@core.state('start')
def start(state):
    core = state.core
    core.colormatch_measurement = M.Measurement.objects(method="closestcolor")[0]
    core.timesince_measurement = M.Measurement.objects(method="timebetween_manual")[0]
    core.deliveredcolor_measurement = M.Measurement.objects(method="closestcolor_manual")[0]
    core.region_inspection = M.Inspection.objects[0]
    return core.state('run')
    

@core.state('run')
def run(state):
    core = state.core
    while True:
      print core.control.state
      if core.control.state == "start":
        core.control.clear_leds()
        core.control.servo_initialize()
        core.control.state = "waitforbutton"

      elif core.control.state == "waitforbutton":
        #while core.control.board.bytes_available():
        #    core.control.board.iterate()
        for co in core.control.controlobjects:
            co.read()

      elif core.control.state == "getmarble":
        core.control.servo_initialize()
        core.control.state = "inspect"

      elif core.control.state == "inspect":
        core.control.servo_inspection()
        core.control.inspecttime = datetime.datetime.utcnow()
        core.control.state = "waitforinspectresults"

      elif core.control.state == "waitforinspectresults":
        gc.collect()
        core.capture()
        realtime.ChannelManager().publish('capture/', { "capture": 1})

        core.inspect()

        r = core.results[-1][0] #NEED TO CHANGE THIS IF WE ADD NEW RESULTS
        f = core.lastframes[-1][0]

        if len(r):
          
          print "Result: ", r[0].string

          if (r[0].string == core.control.matchcolor):
            core.control.state = 'good'
            core.control.servo_good()
            core.control.clear_leds()
            core.control.state = "start"
            td = (datetime.datetime.utcnow() - core.control.starttime)
            timesince = float(td.seconds) + td.microseconds / 1000000.0
            
            
            r2 = M.ResultEmbed(
              result_id = bson.ObjectId(),
              measurement_id = core.control.deliveredcolor_measurement.id,
              measurement_name = core.control.deliveredcolor_measurement.name,
              inspection_id = core.control.region_inspection.id,
              inspection_name = core.control.region_inspection.name,
              numeric = None,
              string = str(core.control.matchcolor)
            )
            
            
            
            r = M.ResultEmbed(
              result_id = bson.ObjectId(),
              measurement_id = core.control.timesince_measurement.id,
              measurement_name = core.control.timesince_measurement.name,
              inspection_id = core.control.region_inspection.id,
              inspection_name = core.control.region_inspection.name,
              numeric = timesince,
              string = str(timesince)
            )
            from util import jsonencode
            print jsonencode([r,r2])
            f.results.extend([r,r2])
            

          else:
            core.control.state = 'notgood'
            core.control.servo_notgood()

        else:
            since = (datetime.datetime.utcnow() - core.control.inspecttime).seconds
            if since > .5:
               core.control.state = 'notgood'
               core.control.servo_bad()
            
        f.save(safe = False)

        
      elif core.control.state == "notgood":
          #core.control.state = 'getmarble'
          core.control.state = 'start' #FIXME TODO NJO

      elif core.control.state == "good":
          core.control.state = 'start'

      else:
        pass
            
      time.sleep(0.05)  
