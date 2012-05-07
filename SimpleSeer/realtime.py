import logging

import gevent
from bson import BSON
from gevent_zeromq import zmq

from socketio.namespace import BaseNamespace

from .Session import Session

log = logging.getLogger(__name__)

class ChannelManager(object):
    __shared_state = { "initialized": False }

    def __init__(self, context):
        '''Yeah, it's a borg'''
        self.__dict__ = self.__shared_state
        if self.initialized: return
        self._channels = {}
        self.config = Session()
        self.context = context
        self.pub_sock = self.context.socket(zmq.PUB)
        self.pub_sock.connect(self.config.pub_uri)

    def __repr__(self):
        l = [ '<ChannelManager>' ]
        for name, channel in self._channels.items():
            l.append('  <Channel %s>' % name)
            for qs in channel:
                l.append('    %r' % qs)
        return '\n'.join(l)

    def publish(self, channel, message):
        self.pub_sock.send(channel, zmq.SNDMORE)
        self.pub_sock.send(BSON.encode(message))

    def subscribe(self, name):
        name=str(name)
        sub_sock = self.context.socket(zmq.SUB)
        sub_sock.connect(self.config.sub_uri)
        sub_sock.setsockopt(zmq.SUBSCRIBE, name)
        log.info('Subscribe to %s: %s', name, id(sub_sock))
        channel = self._channels.setdefault(name, {})
        channel[id(sub_sock)] = sub_sock
        return sub_sock

    def unsubscribe(self, name, sub_sock):
        log.info('Unubscribe to %s: %s', name, id(sub_sock))
        channel = self._channels.get(name, None)
        if channel is None: return
        channel.pop(id(sub_sock), None)
        if not channel:
            self._channels.pop(name, None)

class RealtimeNamespace(BaseNamespace):

    def initialize(self):
        self._channel = None
        self._channel_name = None
        self._greenlet = None
        self._channel_manager = ChannelManager(zmq.Context())

    def disconnect(self, *args, **kwargs):
        if self._channel: self._unsubscribe()
        super(RealtimeNamespace, self).disconnect(*args, **kwargs)

    def on_connect(self, name):
        if self._channel: self._unsubscribe()
        self._subscribe(name)

    def _subscribe(self, name):
        self._channel = self._channel_manager.subscribe(name)
        self._greenlet = gevent.spawn(self._relay)

    def _unsubscribe(self):
        self._greenlet.kill()
        self._channel_manager.unsubscribe(self._channel_name, self._channel)
        self._channel = self._greenlet = self._channel_name = None

    def _relay(self):
        while True:
            self._channel.recv() # discard the envelope
            message = self._channel.recv()
            self.emit('message', BSON(message).to_dict())
