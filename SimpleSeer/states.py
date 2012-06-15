import gevent
from Queue import Queue, Empty
from collections import defaultdict

from .util import Clock

class Core(object):
    '''Implements the core functionality of SimpleSeer
       - capture
       - inspect
       - measure
       - watch
    '''
    class Transition(Exception):
        def __init__(self, state):
            self.state = state

    def __init__(self):
        self._states = {}
        self._cur_state = None
        self._events = Queue()
        self._clock = Clock(1.0, sleep=gevent.sleep)
        self.reset()

    def reset(self):
        start = State(self, 'start')
        self._states = dict(start=start)
        self._cur_state = start

    def state(self, name):
        if name in self._states: return self._states[name]
        s = self._states[name] = State(self, name)
        return s

    def trigger(self, name, data=None):
        self._events.put((name, data))

    def step(self):
        next = self._cur_state = self._cur_state.run(self)
        return next

    def wait(self, name):
        while True:
            try:
                (n,d) = self._events.get(timeout=0.5)
                if n == name: return (n,d)
            except Empty:
                continue
            self._cur_state.trigger(n,d)

    def on(self, state_name, event_name):
        state = self.state(state_name)
        return state.on(event_name)

    def run(self, audit=False):
        audit_trail = []
        while True:
            print self._cur_state
            if self._cur_state is None: break
            if audit: audit_trail.append(self._cur_state.name)
            try:
                self._cur_state = self._cur_state.run(self)
            except self.Transition, t:
                self._cur_state = t.state
        audit_trail.append(None)
        return audit_trail

    def set_rate(self, rate_in_hz):
        self._clock = Clock(rate_in_hz, sleep=gevent.sleep)

    def tick(self):
        self._handle_events()
        self._clock.tick()

    def _handle_events(self):
        while True:
            try:
                (n,d) = self._events.get_nowait()
            except Empty:
                break
            self._cur_state.trigger(n,d)

class Event(object):

    def __init__(self, states, state, channel, message):
        self.states = states
        self.state = state
        self.channel = channel
        self.message = message

class State(object):

    def __init__(self, core, name):
        self.core = core
        self.name = name
        self._events = {}

    def __repr__(self):
        return '<State %s>' % self.name

    def on(self, name):
        def wrapper(callback):
            self._events[name] = callback
            return callback
        return wrapper

    def trigger(self, name, data):
        callback = self._events.get(name)
        if callback is None: return self
        return callback(self, name, data)

    def run(self, core):
        return self

    def transition(self, next):
        raise self.core.Transition(next)

    def __call__(self, func):
        self.run = func
        return func
