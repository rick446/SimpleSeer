from collections import deque
from Queue import Queue, Empty
from cStringIO import StringIO

import zmq
import gevent

from . import models as M
from . import util
from .base import jsondecode, jsonencode
from .camera import StillCamera, VideoCamera

class Core(object):
    '''Implements the core functionality of SimpleSeer
       - capture
       - inspect
       - measure
       - watch
    '''
    _instance=None

    class Transition(Exception):
        def __init__(self, state):
            self.state = state

    def __init__(self, config):
        if Core._instance is not None:
            assert RuntimeError, 'Only one state machine allowed currently'
        Core._instance = self
        self._states = {}
        self._cur_state = None
        self._events = Queue()
        self._clock = util.Clock(1.0, sleep=gevent.sleep)
        self._config = config
        self.config = config #bkcompat for old SeerCore stuff
        self.cameras = []
        self.video_cameras = []
        for cinfo in config.cameras:
            cam = StillCamera(**cinfo)
            video = cinfo.get('video')
            if video is not None:
                cam = VideoCamera(cam, 1.0, **video)
                cam.start()
                self.video_cameras.append(cam)
            self.cameras.append(cam)

        util.load_plugins()
        self.reloadInspections()
        self.lastframes = deque()
        self.framecount = 0
        self.reset()

    @classmethod
    def get(cls):
        return cls._instance

    def reloadInspections(self):
        i = list(M.Inspection.objects)
        m = list(M.Measurement.objects)
        w = list(M.Watcher.objects)
        self.inspections = i
        self.measurements = m
        self.watchers = w

    def start_socket_communication(self):
        '''Listens to ALL messages and trigger()s on them'''
        context = zmq.Context.instance()
        # Setup subscriber
        sub_sock = context.socket(zmq.SUB)
        sub_sock.connect(self._config.sub_uri)
        sub_sock.setsockopt(zmq.SUBSCRIBE, '')
        def g_listener():
            while True:
                name = sub_sock.recv()
                raw_data = sub_sock.recv()
                try:
                    data = jsondecode(raw_data)
                except:
                    continue
                self.trigger(name, data)
        gevent.spawn_link_exception(g_listener)
        # Setup publisher
        self._pub_sock = context.socket(zmq.PUB)
        self._pub_sock.connect(self._config.pub_uri)

    def publish(self, name, data):
        self._pub_sock.send(name, zmq.SNDMORE)
        self._pub_sock.send(jsonencode(data))

    def get_image(self, width, index, camera):
        frame = self.lastframes[index][camera]
        image = frame.image

        if (width):
            image = image.scale(width / float(image.width))

        s = StringIO()
        image.save(s, "jpeg", quality=60)

        return dict(
                content_type='image/jpeg',
                data=s.getvalue())

    def get_config(self):
        return self._config.get_config()

    def reset(self):
        start = State(self, 'start')
        self._states = dict(start=start)
        self._cur_state = start

    def capture(self):
        currentframes = []
        self.framecount += 1

        currentframes = [
            cam.getFrame() for cam in self.cameras ]

        while len(self.lastframes) >= self._config.max_frames:
            self.lastframes.popleft()

        self.lastframes.append(currentframes)
        new_frame_ids = []
        for frame in currentframes:
            new_frame_ids.append(frame.id)
        self.publish('capture/', { "capture": 1, "frame_ids": new_frame_ids})
        return currentframes
        
    def inspect(self, frames = []):
        if not len(frames) and not len(self.lastframes):
            frames = self.capture()
        elif not len(frames):
            frames = self.lastframes[-1]
        
        for frame in frames:
            frame.features = []
            frame.results = []
            for inspection in self.inspections:
                if inspection.parent:  #root parents only
                    continue
                
                if inspection.camera and frame.camera != inspection.camera:
                    #this camera, or all cameras if no camera is specified
                    continue
                
                feats = inspection.execute(frame.image)
                frame.features.extend(feats)
                for m in inspection.measurements:
                    m.execute(frame, feats)
                    
            for watcher in self.watchers:
                watcher.check(frame.results)

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

                
    @property
    def results(self):
        ret = []
        for frameset in self.lastframes:
            results = []
            for f in frameset:
                results += [f.results for f in frameset]
            
            ret.append(results)
            
        return ret

    def get_inspection(self, name):
        return M.Inspection.objects(name=name).next()

    def get_measurement(self, name):
        return M.Measurement.objects(name=name).next()

    def state(self, name):
        if name in self._states: return self._states[name]
        s = self._states[name] = State(self, name)
        return s

    def trigger(self, name, data=None):
        self._events.put((name, data))

    def step(self):
        next = self._cur_state = self._cur_state.run()
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
                self._cur_state = self._cur_state.run()
            except self.Transition, t:
                if isinstance(t.state, State):
                    self._cur_state = t.state
                elif t.state is None:
                    self._cur_state = None
                else:
                    self._cur_state = self.state(t.state)
        audit_trail.append(None)
        return audit_trail

    def set_rate(self, rate_in_hz):
        self._clock = util.Clock(rate_in_hz, sleep=gevent.sleep)
        for cam in self.video_cameras:
            cam.set_rate(rate_in_hz)

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
        self._run = None

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

    def run(self):
        if self._run:
            return self._run(self)
        return self

    def transition(self, next):
        raise self.core.Transition(next)

    def __call__(self, func):
        self._run = func
        return func
