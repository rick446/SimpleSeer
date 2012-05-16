import logging

import zmq
import gevent

log = logging.getLogger(__name__)

class PubSubBroker(gevent.Greenlet):

    def __init__(self, pub_uri, sub_uri):
        # *sigh* you'd think the gevent folks would subclass Greenlet from
        # object, but they don't :-(
        gevent.Greenlet.__init__(self)
        context = zmq.Context.instance()
        log.info('Init pubsub broker with %s,%s', pub_uri, sub_uri)
        self.sub = context.socket(zmq.SUB)
        self.pub = context.socket(zmq.PUB)
        self.sub.bind(pub_uri)
        self.sub.setsockopt(zmq.SUBSCRIBE, '')
        self.pub.bind(sub_uri)
        self.greenlets = []

    def __str__(self):
        return '<PubSubBroker Greenlet>'

    def _run(self):
        while True:
            message = self.sub.recv()
            log.info('relaying on channel %r', message)
            more = self.sub.getsockopt(zmq.RCVMORE)
            while more:
                self.pub.send(message, zmq.SNDMORE)
                message = self.sub.recv()
                more = self.sub.getsockopt(zmq.RCVMORE)
            self.pub.send(message)

        
        
