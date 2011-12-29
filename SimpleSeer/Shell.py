import threading
from base import *
from Session import Session
from SimpleCV import *
import platform

#Load simpleCV libraries
from SimpleCV.Shell import *

def run_shell(shell):
    shell()
    cherrypy.engine.exit()
    
class ShellThread(threading.Thread):
    def run(self):
        scvShell = setup_shell()
        sys.exit(run_shell(scvShell))

from SimpleSeer import SimpleSeer
from Inspection import Inspection
from Measurement import Measurement
from Result import Result
from Web import Web
from Frame import Frame
from FrameFeature import FrameFeature
