import threading
from base import *
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

from .SimpleSeer import SimpleSeer
from .models import *
