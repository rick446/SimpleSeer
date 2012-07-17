import time
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
        self.options = options
        if self.use_gevent:
            import gevent_zeromq
            from gevent import monkey
            monkey.patch_all()
            gevent_zeromq.monkey_patch()
        # These imports need to happen *after* monkey patching
        from SimpleSeer.Session import Session
        from SimpleSeer import models as M
        self._configure_logging()
        self.session = Session(options.config)
        if self.remote_seer:
            from SimpleSeer.SimpleSeer import SimpleSeer as SS
            SS(disable=True)
        if self.session.mongo.get('is_slave'):
            M.base.SimpleDoc.meta['auto_create_index'] = False
        if options.profile_heap: self._start_profile_heap()

    def run(self):
        '''Actually run the command'''
        raise NotImplementedError, 'run'

    def _configure_logging(self):
        import logging
        if self.options.logging:
            logging.config.fileConfig(self.options.logging)
        else:
            logging.basicConfig()
        self.log = logging.getLogger(__name__)

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
    
