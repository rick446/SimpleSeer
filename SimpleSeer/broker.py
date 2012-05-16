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
        log.info('Init pubsub broker with PUB=%s,SUB=%s', pub_uri, sub_uri)
        self.sub = context.socket(zmq.SUB)
        self.pub = context.socket(zmq.PUB)
        self.sub.bind(pub_uri)
        self.pub.bind(sub_uri)
        self.sub.setsockopt(zmq.SUBSCRIBE, '')

    def __str__(self):
        return '<PubSubBroker Greenlet>'

    def _run(self):
        relay(self.sub, self.pub, '>>')
        
def relay(s1, s2, prefix):
    log.info('relay %s', prefix)
    while True:
        multipart_msg = s1.recv_multipart()
        log.info('relay %s %r', prefix, multipart_msg[0])
        s2.send_multipart(multipart_msg)
