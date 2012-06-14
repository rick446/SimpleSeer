import gevent
from collections import defaultdict

class State(object):

    def __init__(self, states, name):
        self._states = states
        self._name = name
        self._edges = {}

    def on(self, event=None):
        def wrapper_event(callback):
            self._edges[event] = callback
            return callback
        def wrapper_idle(callback):
            self.idle = callback
            return callback
        if event:
            return wrapper_event
        else:
            return wrapper_idle

    def trigger(self, event, data):
        transition = self._edges.get(event, None)
        if transition is None: return self
        return transition(self._states, self, event, data)

    def idle(self, states, state):
        gevent.sleep(0)
        return self

class States(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self._cur = State(self, 'start')
        self._states = dict(start=self._cur)

    def on(self, state, event=None):
        s = self.get(state)
        return s.on(event)

    def trigger(self, event, data=None):
        if data is None: data = {}
        self._cur = self._cur.trigger(event, data)
        if isinstance(self._cur, basestring):
            self._cur = self.get(self._cur)

    def run(self):
        while self._cur:
            self._cur = self._cur.idle(self, self._cur)

    def get(self, name):
        s = self._states.get(name, None)
        if s is None:
            s = self._states[name] = State(self, name)
        return s

    def __getattr__(self, name):
        if name.startswith('_'):
            return super(States, self).__getattr__(name)
        return self.get(name)
