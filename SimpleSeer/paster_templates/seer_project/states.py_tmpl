#-*-python-*-
# This is the state machine file. Configure it to suit your tastes.

import gc
from SimpleSeer import models as M
from SimpleSeer.Session import Session

config = Session()
if config.poll_rate:
    RATE=config.poll_rate
else:
    RATE = 0.5

@core.state('start')
def start(state):
    core = state.core
    core.set_rate(RATE)
    return state.core.state('run')

@core.state('run')
def run(state):
    core = state.core
    while True:
        core.tick()
        gc.collect()
        frames = core.capture()
        for frame in frames:
            core.process(frame)
            if config.record_all:
                frame.save()


@core.on('run', 'rate/')
def set_rate(state, name, data):
    state.core.set_rate(data['rate'])
    state.transition('run')
