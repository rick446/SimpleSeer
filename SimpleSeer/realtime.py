import logging

import zmq
import gevent
import gevent.coros

from socketio.namespace import BaseNamespace

from .Session import Session
from .base import jsonencode, jsondecode

log = logging.getLogger(__name__)

class ChannelManager(object):
    __shared_state = { "initialized": False }

    def __init__(self, context=None):
        '''Yeah, it's a borg'''
        self.__dict__ = self.__shared_state
        if self.initialized: return
        self.initialized = True
        self._channels = {}
        self.config = Session()
        self._lock = gevent.coros.RLock()
        self.context = context or zmq.Context.instance()
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
        '''Publish a JSON message over the channel. Note that while it would be
        nice to use a compact and fast encoding like BSON, these messages need to
        get relayed down to the browser, which is expecting JSON.
        '''
        with self._lock:
            self.pub_sock.send(channel, zmq.SNDMORE)
            self.pub_sock.send(jsonencode(message))

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
        log.info('Unsubscribe to %s: %s', name, id(sub_sock))
        channel = self._channels.get(name, None)
        if channel is None: return
        channel.pop(id(sub_sock), None)
        if not channel:
            self._channels.pop(name, None)

class RealtimeNamespace(BaseNamespace):

    def initialize(self):
        self._channels = {}  # _channels[name] = (socket, greenlet)
        self._channel_manager = ChannelManager()

    def disconnect(self, *args, **kwargs):
        for name in self._channels.keys():
            self._unsubscribe(name)
        super(RealtimeNamespace, self).disconnect(*args, **kwargs)

    def on_subscribe(self, name):
        self._subscribe(name)

    def on_unsubscribe(self, name):
        self._unsubscribe(name)

    def _subscribe(self, name):
        socket = self._channel_manager.subscribe(name)
        greenlet = gevent.spawn_link_exception(self._relay, name, socket)
        self._channels[name] = (socket, greenlet)

    def _unsubscribe(self, name):
        if name not in self._channels: return
        socket, greenlet = self._channels.pop(name)
        greenlet.kill()
        self._channel_manager.unsubscribe(name, socket)

    def _relay(self, name, socket):
        while True:
            channel = socket.recv() # discard the envelope
            message = socket.recv()
            self.emit('message:' + name, dict(
                    channel=channel,
                    data=jsondecode(message)))
