
import threading
import datetime
import time

import models as M
import gc
import bson
import realtime as realtime


class ControlObject:
   """
    An abstract class for all objects -- controls Arduino pin assignment 
    and previous state

    This needs to be fleshed out

   """
   pin = '' 
   state = 0
   statechange = False
   controller = ''
   handlers = []

   def __init__(self, pin, C, handlers = []):
       self.controller = C
       self.pin = C.board.get_pin('d:%d:i' % pin)
       self.pin.enable_reporting()
       self.state = False
       self.handlers = handlers

   def read(self): 
         newstate = self.pin.read()
         if newstate != None and newstate != self.state: #need to add some "smoothing" here probably
             self.state = newstate
             self.fire(newstate) 

   def fire(self, state):
       for function_ref in self.handlers:
          function_ref(state)   
           

class ControlWatcher(threading.Thread):
    def run(self):
        while True:
          print self.control.state

          if self.control.state == "start":
            self.control.servo_initialize()
            self.control.state = "waitforbutton"

          elif self.control.state == "waitforbutton":
            for co in self.control.controlobjects:
                co.read()

          elif self.control.state == "getmarble":
            self.control.servo_initialize()
            self.control.state = "inspect"

          elif self.control.state == "inspect":
            self.control.servo_inspection()
            self.control.inspecttime = datetime.datetime.utcnow()
            self.control.state = "waitforinspectresults"

          elif self.control.state == "waitforinspectresults":
            gc.collect()
            ss = self.control.SS    
            ss.capture()
            realtime.ChannelManager().publish('capture/', { "capture": 1})

            ss.inspect()
            ss.check()

            r = ss.results[-1][0] #NEED TO CHANGE THIS IF WE ADD NEW RESULTS
            f = ss.lastframes[-1][0]

            if len(r):
              
              print "Result: ", r[0].string

              if (r[0].string == self.control.matchcolor):
                self.control.state = 'good'
                self.control.servo_good()
                self.control.state = "start"
                td = (datetime.datetime.utcnow() - self.control.starttime)
                timesince = float(td.seconds) + td.microseconds / 1000000.0
                
                
                r2 = M.ResultEmbed(
                  result_id = bson.ObjectId(),
                  measurement_id = self.control.deliveredcolor_measurement.id,
                  measurement_name = self.control.deliveredcolor_measurement.name,
                  inspection_id = self.control.region_inspection.id,
                  inspection_name = self.control.region_inspection.name,
                  numeric = None,
                  string = str(self.control.matchcolor)
                )
                
                
                
                r = M.ResultEmbed(
                  result_id = bson.ObjectId(),
                  measurement_id = self.control.timesince_measurement.id,
                  measurement_name = self.control.timesince_measurement.name,
                  inspection_id = self.control.region_inspection.id,
                  inspection_name = self.control.region_inspection.name,
                  numeric = timesince,
                  string = str(timesince)
                )
                from util import jsonencode
                print jsonencode([r,r2])
                f.results.extend([r,r2])
                
                
              elif (r[0].string == "purple"):
                self.control.state = 'notgood'
                self.control.servo_bad() 
              else:
                self.control.state = 'notgood'
                self.control.servo_notgood()

            else:
                since = (datetime.datetime.utcnow() - self.control.inspecttime).seconds
                if since > .5:
                   self.control.state = 'notgood'
                   self.control.servo_bad()
                   self.control.servo_mix()
                
            f.save(safe = False)
  
            
          elif self.control.state == "notgood":
              self.control.state = 'getmarble'

          elif self.control.state == "good":
              self.control.state = 'start'

          else:
            pass
                
            
            
          time.sleep(0.1)

  
     
class Controls(object):
    iterator = ''
    board = ''
    state = ''
    servo = None

    #servo setup
    fwheel = None
    fwheel_pos1 = 165
    fwheel_pos2 = 115
    fwheel_pos3 = 51
    fwheel_pos4 = 25
    fwheel_pos5 = 0

    rwheel = None
    rwheel_pos1 = 110
    rwheel_pos2 = 137
    rwheel_pos3 = 165

    awheel_right = 0
    awheel_stop = 158
    awheel_left = 180

    SLEEPTIME = 1
    aggtime = 15
    ROTATE_TIME = 1

    
    def firecolor(self, state, color):
        if state == True and self.state == 'waitforbutton':
            print color, " button pressed"
            self.state = "inspect"
            self.matchcolor = color
            self.starttime = datetime.datetime.utcnow()
            
    def fire_green(self, state):
        self.firecolor(state, "green")

    def fire_yellow(self, state):
        self.firecolor(state, "yellow")
    
    def fire_orange(self, state):
        self.firecolor(state, "orange")
 
    def fire_red(self, state):
        self.firecolor(state, "red")


    def servo_initialize(self):
        self.fwheel.write(self.fwheel_pos2)
        self.rwheel.write(self.rwheel_pos3)
        time.sleep(self.SLEEPTIME)

    def servo_inspection(self):
        self.fwheel.write(self.fwheel_pos3 - 10)
        time.sleep(0.2)
        self.fwheel.write(self.fwheel_pos1)
        self.rwheel.write(self.rwheel_pos3)
        time.sleep(self.SLEEPTIME)


    def servo_bad(self):
        self.fwheel.write(self.fwheel_pos3)
        self.rwheel.write(self.rwheel_pos1)
        time.sleep(self.SLEEPTIME)

    def servo_notgood(self):
        self.fwheel.write(self.fwheel_pos4)
        self.rwheel.write(self.rwheel_pos2)
        time.sleep(self.SLEEPTIME)

    def servo_good(self):
        self.fwheel.write(self.fwheel_pos5)
        time.sleep(0.1)
        self.fwheel.write(self.fwheel_pos5+10)
        time.sleep(0.05)
        self.fwheel.write(self.fwheel_pos5)
        self.rwheel.write(self.rwheel_pos3)
        time.sleep(self.SLEEPTIME)

    def servo_mix(self):
        self.awheel.write(self.awheel_right)
        time.sleep(self.ROTATE_TIME)
        self.awheel.write(self.awheel_left)
        time.sleep(self.ROTATE_TIME * 3)
        self.awheel.write(self.awheel_stop)
      


    def __init__(self, config, SS):
       from pyfirmata import Arduino, util, SERVO
       self.SS = SS
       self.board = Arduino(config['board'])
       self.iterator = util.Iterator(self.board)
       self.iterator.daemon = True
       self.iterator.start()
       self.fwheel = self.board.get_pin('d:11:p')
       self.fwheel.mode = SERVO
       self.rwheel = self.board.get_pin('d:10:p')
       self.rwheel.mode = SERVO
       self.awheel = self.board.get_pin('d:3:p')
       self.awheel.mode = SERVO
       self.awheel.write(self.awheel_stop)
       
       self.state = 'start'
       
       self.controlobjects = [
          ControlObject(9, self, [self.fire_red]),
          ControlObject(8, self, [self.fire_orange]),
          ControlObject(12, self, [self.fire_yellow]),
          ControlObject(13, self, [self.fire_green])
       ]

       self.colormatch_measurement = M.Measurement.objects(method="closestcolorml")[0]
       self.timesince_measurement = M.Measurement.objects(method="timebetween_manual")[0]
       self.deliveredcolor_measurement = M.Measurement.objects(method="closestcolor_manual")[0]
       self.region_inspection = M.Inspection.objects[0]
       self.SS = SS

       if not "debug" in config:
         self.cw = ControlWatcher()
         self.cw.control = self
         self.cw.daemon = True
         self.cw.start()




    
