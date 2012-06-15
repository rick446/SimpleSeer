import time
import gevent
import unittest

import mock

from SimpleSeer.states import Core

class TestStateMachine(unittest.TestCase):

    def setUp(self):
        self.core = Core()

    def test_single_frame(self):
        self.core.cameras = [ mock.Mock() ]

        @self.core.state('start')
        def capture_frame(core):
            core.wait('capture-frame')
            core.cameras[0].capture()
            return core.state('start')

        self.core.trigger('capture-frame')
        self.assertEqual(
            self.core.state('start'),
            self.core.step())
        self.core.cameras[0].capture.assert_called_with()

    def test_motion_threshold(self):
        slow_rate = 10.0
        fast_rate = 50.0
        threshold0 = 50
        threshold1 = 5
        motion = mock.Mock()
        result = mock.Mock()
        result.featuredata = dict(motion=10)
        motion.execute = mock.Mock(return_value=[result])
        self.core.get_inspection = mock.Mock(return_value=motion)
        self.core.cameras = [ mock.Mock() ]
        def capture():
            print time.time(), 'Capture'
            capture.call_count += 1
        capture.call_count = 0
        self.core.cameras[0].capture = capture

        @self.core.state('start')
        def slow_state(core):
            core.set_rate(slow_rate)
            motion = core.get_inspection('motion')
            while True:
                core.tick()
                frame = core.cameras[0].capture()
                features = motion.execute(frame)
                if features[0].featuredata['motion'] > threshold0:
                    return core.state('fast')

        @self.core.state('fast')
        def fast_state(core):
            core.set_rate(fast_rate)
            motion = core.get_inspection('motion')
            while True:
                core.tick()
                frame = core.cameras[0].capture()
                features = motion.execute(frame)
                if features[0].featuredata['motion'] < threshold1:
                    return core.state('start')

        @self.core.on('start', 'terminate')
        @self.core.on('fast', 'terminate')
        def terminate(state, name, data):
            state.transition(None)

        gl = gevent.spawn_link_exception(self.core.run, audit=True)
        gevent.sleep(0.2)
        print 'Set motion to 55'
        result.featuredata['motion'] = 55
        gevent.sleep(0.2)
        print 'Set motion to 4'
        result.featuredata['motion'] = 4
        gevent.sleep(0.2)
        print 'Call terminate'
        self.core.trigger('terminate')
        trail = gl.get()
        self.assertEqual(trail, ['start', 'fast', 'start', None])
        num_frames = self.core.cameras[0].capture.call_count
        print num_frames
        self.assertGreater(num_frames, 12)
        self.assertLess(num_frames, 15)

    def test_conditional_inspections(self):
        threshold = 20
        inspections = dict(
            motion = mock.Mock(),
            blob = mock.Mock())
        featuredata = dict(motion=10)
        self.core.get_inspection = lambda name: inspections[name]
        self.core.cameras = [ mock.Mock() ]
        def capture():
            print time.time(), 'Capture'
            capture.call_count += 1
        capture.call_count = 0
        def blob_ex(frame):
            print 'Blob'
            blob_ex.call_count += 1
        blob_ex.call_count = 0
        def motion_ex(frame):
            print 'Motion'
            motion_ex.call_count += 1
            result = mock.Mock()
            result.featuredata = featuredata
            return [result]
        motion_ex.call_count = 0
        inspections['motion'].execute = motion_ex
        inspections['blob'].execute = blob_ex
        self.core.cameras[0].capture = capture

        @self.core.state('start')
        def start_state(core):
            core.set_rate(10.0)
            motion = core.get_inspection('motion')
            blob = core.get_inspection('blob')
            camera = core.cameras[0]
            while True:
                core.tick()
                frame = camera.capture()
                features = motion.execute(frame)
                if features[0].featuredata['motion'] > threshold:
                    blob.execute(frame)

        @self.core.on('start', 'terminate')
        @self.core.on('fast', 'terminate')
        def terminate(state, name, data):
            state.transition(None)

        gl = gevent.spawn_link_exception(self.core.run)
        gevent.sleep(0.2)
        print '===> Set motion to 55'
        featuredata['motion'] = 55
        gevent.sleep(0.2)
        print '===> Set motion to 4'
        featuredata['motion'] = 4
        gevent.sleep(0.2)
        print '===> Call terminate'
        self.core.trigger('terminate')
        gl.join()
        motion_calls = inspections['motion'].execute.call_count
        blob_calls = inspections['blob'].execute.call_count
        self.assertGreater(motion_calls, blob_calls)
        self.assertGreater(blob_calls, 0)
