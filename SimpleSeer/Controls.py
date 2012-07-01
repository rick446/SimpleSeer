from glob import glob
import time
import datetime

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
       self.pin_id = pin
       self.pin = C.board.get_pin('d:%d:i' % pin)
       self.pin.enable_reporting()
       self.state = False
       self.handlers = handlers

   def read(self): 
         newstate = self.pin.read()
         if newstate != None and newstate != self.state and newstate:
             self.fire(newstate) 
         self.state = newstate

   def fire(self, state):
       for function_ref in self.handlers:
          function_ref(state)   
           
       
class Controls(object):
    iterator = ''
    board = ''
    state = ''
    servo = None

    #servo setup
    fwheel = None
    fwheel_pos1 = 85
    fwheel_pos2 = 150
    fwheel_pos4 = 22
    fwheel_pos5 = 0

    rwheel = None
    rwheel_pos2 = 97
    rwheel_pos3 = 115

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
        self.board.digital[6].write(1)

    def fire_yellow(self, state):
        self.firecolor(state, "yellow")
        self.board.digital[5].write(1)
    
    def fire_orange(self, state):
        self.firecolor(state, "orange")
        self.board.digital[4].write(1)
 
    def fire_red(self, state):
        self.firecolor(state, "red")
        self.board.digital[3].write(1)

    def fire_purple(self, state):
        self.firecolor(state, "purple")
        self.board.digital[2].write(1)
        
    def servo_initialize(self):
        self.fwheel.write(self.fwheel_pos2)
        self.rwheel.write(self.rwheel_pos3)
        time.sleep(self.SLEEPTIME)

    def servo_inspection(self):
        self.fwheel.write(self.fwheel_pos1)
        self.rwheel.write(self.rwheel_pos3)
        time.sleep(self.SLEEPTIME)


    def servo_bad(self):
        self.servo_notgood()

    def servo_notgood(self):
        self.rwheel.write(self.rwheel_pos2)
        
        self.fwheel.write(self.fwheel_pos4 - 5)
        time.sleep(0.1)
        
        self.fwheel.write(self.fwheel_pos4)
        time.sleep(self.SLEEPTIME)

    def servo_good(self):
        self.rwheel.write(self.rwheel_pos3)
        self.fwheel.write(self.fwheel_pos5)
        time.sleep(0.1)
        self.fwheel.write(self.fwheel_pos5+10)
        time.sleep(0.05)
        self.fwheel.write(self.fwheel_pos5)
        time.sleep(self.SLEEPTIME)

    def clear_leds(self):
        for i in range(2,7):
            self.board.digital[i].write(0)


    def __init__(self, config):
       from pyfirmata import Arduino, util, SERVO
       boardglob = config['board']
       boards = glob(config['board'])
       if not len(boards):
              raise Exception("No Arduino found")
       
       self.board = Arduino(boards[0])
       self.iterator = util.Iterator(self.board)
       self.iterator.daemon = True
       self.iterator.start()
       self.fwheel = self.board.get_pin('d:11:p')
       self.fwheel.mode = SERVO
       self.rwheel = self.board.get_pin('d:10:p')
       self.rwheel.mode = SERVO
       
       
       self.state = 'start'
       
       self.controlobjects = [
          ControlObject(7, self, [self.fire_purple]),
          ControlObject(8, self, [self.fire_red]),
          ControlObject(9, self, [self.fire_orange]),
          ControlObject(12, self, [self.fire_yellow]),
          ControlObject(13, self, [self.fire_green])
       ]



    
