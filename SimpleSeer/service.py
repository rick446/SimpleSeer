from cStringIO import StringIO
from itertools import chain

import Pyro4

from . import models as M
from . import util
from .Session import Session

class SeerProxy2(object):
    '''It's a proxy of a Pyro4.Proxy, so it's a proxy^2. Get it?'''
    __shared_state = { "initialized": False }

    def __init__(self):
        self.__dict__ = self.__shared_state
        if self.initialized: return
        self.initialized = True
        self.plugins = util.load_plugins()
        try:
            self._proxy = Pyro4.Proxy('PYRONAME:sightmachine.seer')
            self._proxy.get_config()
        except Pyro4.errors.NamingError, err:
            self._proxy = None
            self._proxy_error = err

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
        if self._proxy:
            id = self.get_frame_id(index, camera)
        if id is None: return None
        return M.Frame.objects.get(id=id)

    def get_image(self, width, index=-1, camera=0):
        if self._proxy:
            return self._proxy.get_image(width, index, camera)
        cname = Session().camera_name(camera)
        q = M.Frame.objects(camera=cname)
        if index < 0:
            q = q.order_by('-capturetime')
        else:
            q = q.order_by('capturetime')
            index = -(index + 1)
        for frame in q:
            if frame.has_image_data():
                index += 1
                if index == 0:
                    image = frame.image
                    break
        else:
            return None
        if width:
            image = image.scale(width / float(image.width))
        sio = StringIO()
        image.save(sio, 'jpeg', quality=60)
        return dict(
            content_type='image/jpeg', data=sio.getvalue())

    def __getattr__(self, name):
        if self._proxy is None:
            raise self._proxy_error
        return getattr(self._proxy, name)
