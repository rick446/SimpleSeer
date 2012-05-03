import logging

import gevent.queue

from socketio.namespace import BaseNamespace

log = logging.getLogger(__name__)

class ChannelManager(object):
    __shared_state = { "initialized": False }

    def __init__(self):
        '''Yeah, it's a borg'''
        self.__dict__ = self.__shared_state
        if self.initialized: return
        self._channels = {}

    def __repr__(self):
        l = [ '<ChannelManager>' ]
        for name, channel in self._channels.items():
            l.append('  <Channel %s>' % name)
            for qs in channel:
                l.append('    %r' % qs)
        return '\n'.join(l)

    def publish(self, channel, message):
        for q in self._channels.get(channel, {}).values():
            q.put(message)

    def subscribe(self, name):
        q = gevent.queue.Queue()
        q.channel = name
        log.info('Subscribe to %s: %s', name, id(q))
        channel = self._channels.setdefault(name, {})
        channel[id(q)] = q
        return q

    def unsubscribe(self, q):
        log.info('Unubscribe to %s: %s', q.channel, id(q))
        channel = self._channels.get(q.channel, None)
        if channel is None: return
        channel.pop(id(q), None)
        if not channel:
            self._channels.pop(q.channel, None)

class RealtimeNamespace(BaseNamespace):

    def initialize(self):
        self._channel = None
        self._greenlet = None
        self._channel_manager = ChannelManager()

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
        self._channel_manager.unsubscribe(self._channel)
        self._channel = self._greenlet = None

    def _relay(self):
        while True:
            message = self._channel.get()
            self.emit('message', message)
