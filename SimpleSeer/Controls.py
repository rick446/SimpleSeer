from glob import glob
import time
import datetime
import gevent
import gevent.monkey as monkey

from realtime import ChannelManager
from pyfirmata import Arduino, util, SERVO

from .base import jsondecode

class FakePin(object):
    id = None
    
    def __init__(self, pin):
        id = pin

    def read(self):
        return False
        
    def write(self):
        return False

class Fakemata:
    def get_pin(self, id):
        return FakePin(id)

class Button:
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

    def __init__(self, pin, message, board):
        self.pin_id = pin
        self.board = board
        self.pin = self.board.get_pin('d:%d:i' % pin)
        self.pin.enable_reporting()
        self.message = message
        self.state = False

    def read(self): 
        newstate = self.pin.read()
        if newstate != None and newstate != self.state and newstate:
            self.fire(newstate) 
        self.state = newstate

    def fire(self, state):
        ChannelManager().publish("ControlInput/", self.message)
       
class Servo(object):
    pin = None
    position = 0
    board = None
    id = None
    
    def __init__(self, pin_id, board):
        self.pin_id = id
        self.board = board
        self.pin = self.board.get_pin('d:%d:p' % pin_id)
        self.pin.mode = SERVO
       
    def moveTo(self, value):
        self.pin.write(value)
        position = value
        print "moving servo"
       
class DigitalOut(object):
    pin = None
    state = False
    board = None
    id = None
    
    def __init__(self, pin_id, board):
        self.board = board
        self.pin = self.board.digital[pin_id]
        self.pin.write(0)
        self.state = False
    
    def write(self, val):
        print "writing to pin"
        if val:
            self.on()
        else:
            self.off()
        
    def on(self):
        self.state = True
        self.pin.write(1)
        
    def off(self):
        self.state = False
        self.pin.write(0)
        
       
class Controls(object):
    iterator = ''
    board = ''
    servos = None
    digitalouts = None
    buttons = None
    subsock = None

    def __init__(self, session):

        monkey.patch_socket() 
        import gevent_zeromq
        gevent_zeromq.monkey_patch()
         #we do use greenlets, but only patch sock stuff
        #other stuff messes up the

        config = session.arduino 
        boardglob = config['board']
        boards = glob(boardglob)
        if not len(boards):
              raise Exception("No Arduino found")
        
        self.board = Arduino(boards[0])
        #self.iterator = util.Iterator(self.board)
        #self.iterator.daemon = True
        #self.iterator.start()

        #initialize servo objects
        self.servos = {}
        if config["servos"]:
            for servo in config["servos"]:
                self.servos[servo['name']] = Servo(servo['pin'], self.board)

        #initialize light objects
        self.digitalouts = {}
        if config["digitalouts"]:
            for do in config["digitalouts"]:
                self.digitalouts[do['name']] = DigitalOut(do['pin'], self.board)

        if config["digitalouts"] or config["servos"]:
            self.subsock = ChannelManager().subscribe("ControlOutput/")

        self.buttons = []
        if config["buttons"]:
            for button in config["buttons"]:
                self.buttons.append(Button(button['pin'], button['message'], self.board))

    def checkSubscription(self):
        if not self.subsock:
            return
            
        while True:
            channel = self.subsock.recv()
            message = self.subsock.recv()            
            message = jsondecode(message)
            
            for name,value in message.items():
                if name in self.servos:
                    self.servos[name].moveTo(value)
                elif name in self.digitalouts:
                    self.digitalouts[name].write(value)
            gevent.sleep(0)

    def run(self):
        if self.subsock and len(self.buttons):
            gevent.spawn_link_exception(Controls.checkSubscription, self)
        elif self.subsock:
            self.checkSubscription()
            return
        
        while True:
            while self.board.bytes_available():
                self.board.iterate()
            #make sure we have a clean buffer before bouncing the buttons    
            for b in self.buttons:
                b.read()
            
            gevent.sleep(0)



