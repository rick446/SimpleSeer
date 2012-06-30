import gc
from SimpleSeer import models as M

RATE=0.5

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
            process(frame)
            frame.save()


@core.on('run', 'rate.')
def set_rate(state, name, data):
    state.core.set_rate(data['rate'])
    state.transition('run')

def process(frame):
    frame.features = []
    frame.results = []
    for inspection in M.Inspection.objects:
        if inspection.parent:
            return
        if inspection.camera and inspection.camera != frame.camera:
            return
        results = inspection.execute(frame.image)
        frame.features += results
        for m in inspection.measurements:
            m.execute(frame, results)
