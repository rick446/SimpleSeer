import logging

import gevent
from gevent_zeromq import zmq

log = logging.getLogger(__name__)

class PubSubBroker(object):

    def __init__(self, pub_uri, sub_uri):
        context = zmq.Context.instance()
        log.info('Init pubsub broker with %s,%s', pub_uri, sub_uri)
        self.sub = context.socket(zmq.SUB)
        self.pub = context.socket(zmq.PUB)
        self.sub.bind(pub_uri)
        self.sub.setsockopt(zmq.SUBSCRIBE, '')
        self.pub.bind(sub_uri)
        self.greenlets = []

    def relay(self, s1, s2):
        while True:
            message = s1.recv()
            more = s1.getsockopt(zmq.RCVMORE)
            while more:
                s2.send(message, zmq.SNDMORE)
                message = s1.recv()
                more = s1.getsockopt(zmq.RCVMORE)
            s2.send(message)

    def start(self):
        self.greenlets = [
            gevent.spawn(self.relay, self.sub, self.pub) ]

    def join(self):
        gevent.joinall(self.greenlets)

    def serve_forever(self):
        self.start()
        self.join()
        
        
