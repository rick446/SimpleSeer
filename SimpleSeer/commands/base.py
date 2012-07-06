import time
import logging
import threading

import gevent
import guppy

class Command(object):
    'A simpleseer subcommand'
    use_gevent=True
    remote_seer=True

    def __init__(self, subparser):
        '''Add any options here'''

    def configure(self, options):
        from SimpleSeer import models as M
        from SimpleSeer.Session import Session
        self.options = options
        self.log = logging.getLogger(__name__)
        self.session = Session(options.config)
        if self.use_gevent:
            from gevent import monkey
            monkey.patch_all()
            import gevent_zeromq
            gevent_zeromq.monkey_patch()
        if self.remote_seer:
            from SimpleSeer.SimpleSeer import SimpleSeer as SS
            SS(disable=True)
        if self.session.mongo.get('is_slave'):
            M.base.SimpleDoc.meta['auto_create_index'] = False
        if options.profile_heap: self._start_profile_heap()

    def run(self):
        '''Actually run the command'''
        raise NotImplementedError, 'run'

    @classmethod
    def simple(cls, use_gevent=True, remote_seer=True):
        '''Create a simple command. Used as a decorator'''
        def decorator(run_func):
            return type(
                run_func.__name__,
                (cls,),
                dict(run=run_func,
                     __doc__=run_func.__doc__))
        return decorator

    def _start_profile_heap(self):
        def profiler():
            while True:
                h = guppy.hpy()
                print h.heap()
                sleep(5)
        if self.use_gevent:
            sleep = gevent.sleep
            gevent.spawn(profiler, gevent.sleep)
        else:
            sleep = time.sleep
            t = threading.Thread(target=profiler)
            t.daemon = True
            t.start()
    
