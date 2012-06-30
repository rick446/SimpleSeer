import gc
from SimpleSeer import models as M
from SimpleSeer.Controls import Controls
import time

RATE=0.5

@core.state('start')
def start(state):
    core = state.core
    controls = Controls(core.config.arduino, core)
    return core.state('run')
    

@core.state('run')
def run(state):
    core = state.core
    while True:
        time.sleep(1)
