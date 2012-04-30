import threading
from base import *
from Session import Session
from SimpleCV import *
import platform

#Load simpleCV libraries
from SimpleCV.Shell import *

def run_shell(parent, shell):
    shell()
    parent.stop()
    #~ cherrypy.engine.exit()
    
class ShellThread(threading.Thread):

    def __init__(self):
        super(ShellThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        scvShell = setup_shell()
        sys.exit(run_shell(self, scvShell))

from SimpleSeer import SimpleSeer
from Inspection import Inspection
from Measurement import Measurement
from Watcher import Watcher
from Result import Result
from OLAP import OLAP
#~ from Web import Web
#from Web2 import Web2
from Frame import Frame
from FrameFeature import FrameFeature
