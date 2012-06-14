import gevent
import unittest

import mock

from SimpleSeer import states

class TestStateMachine(unittest.TestCase):

    def setUp(self):
        self.states = states.States()

    def tearDown(self):
        self.states.clear()

    def test_callback(self):
        called_with = []
        @self.states.on('start', 'test')
        def callback(*args, **kwargs):
            called_with.append((args, kwargs))
            return None
        self.states.trigger('test')
        self.states.run()
        self.assertEqual(called_with, [
                ((self.states, self.states.start, 'test', {}), {}) ])

    def test_capture_one_frame(self):
        seer = mock.Mock()
        @self.states.on('start', 'test-channel')
        def callback(states, state, event, message):
            seer.run(frames=1)
        self.states.trigger('test-channel', {})
        self.states.run()
        seer.run.assert_called_with(frames=1)

    def test_ping_pong(self):
        @self.states.on('start')
        def start_state(states, state):
            return states.first
        @self.states.on('first', 'se')
        def first(states, seer, message):
            print 'first'
            gevent.sleep(0.5)
            return states.second
        @self.states.on('first', 'second')
        def high_speed(states, seer, message):
            print 'second'
            gevent.sleep(0.5)
            states.trigger('first')
        @self.states.on('terminate')
        def terminate(states, seer, message):
            print 'terminate'
            self.states.clear()
        def terminate_in(secs):
            gevent.sleep(secs)
            self.states.trigger('terminate')
        self.states.trigger('first')
        gevent.spawn(terminate_in, 2)
        self.states.run()
