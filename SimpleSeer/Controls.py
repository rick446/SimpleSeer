
import threading
import time
import util

import models as M


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
            for co in self.control.controlobjects:
                co.read()
            
            
            
            
            time.sleep(0.1)

  
     
class Controls(object):
    iterator = ''
    board = ''
    state = ''
    
    def fire_color(self, state, color):
        if state == True and self.state == 'init':
            print color, " button pressed"
            self.state == "inspect"
            self.matchcolor = color
            self.statetime = time.time() 
    
    def fire_green(self, state):
        self.firecolor(state, "green")

    def fire_yellow(self, state):
        self.firecolor(state, "yellow")
    
    def fire_orange(self, state):
        self.firecolor(state, "orange")
 
    def fire_red(self, state):
        self.firecolor(state, "red")




    def __init__(self, config, SS):
       from pyfirmata import Arduino, util

       self.board = Arduino(config['board'])
       self.iterator = util.Iterator(self.board)
       self.iterator.daemon = True
       self.iterator.start()
       
       self.state = 'init'
       
       self.controlobjects = [
          ControlObject(7, self, [self.fire_green]),
          ControlObject(8, self, [self.fire_yellow]),
          ControlObject(12, self, [self.fire_orange]),
          ControlObject(13, self, [self.fire_red])
       ]
       
       self.SS = SS
       self.cw = ControlWatcher()
       self.cw.control = self
       self.cw.daemon = True
       self.cw.start()
