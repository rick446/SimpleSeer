from itertools import chain

import Pyro4

from . import models as M
from . import util

class SeerProxy2(object):
    '''It's a proxy of a Pyro4.Proxy, so it's a proxy^2. Get it?'''
    __shared_state = { "initialized": False }

    def __init__(self):
        self.__dict__ = self.__shared_state
        if self.initialized: return
        self.initialized = True
        self._proxy = Pyro4.Proxy('PYRONAME:sightmachine.seer')
        self._proxy.get_config()
        self.plugins = util.load_plugins()

    @property
    def lastframes(self):
        frame_ids = self.get_last_frame_ids()
        all_ids = [ id for id in chain(*frame_ids)
                    if id is not None ]
        frame_index = dict(
            (f.id, f) for f in M.Frame.objects(id__in=all_ids))
        frames = [
            [ frame_index.get(id) for id in ids ]
            for ids in frame_ids ]
        return frames

    def get_frame(self, index=-1, camera=0):
        id = self.get_frame_id(index, camera)
        if id is None: return None
        objs = M.Frame.objects(id=id)
        if objs: return objs[0]
        return None

    def __getattr__(self, name):
        return getattr(self._proxy, name)
