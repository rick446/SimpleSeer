import threading
import traceback
from cStringIO import StringIO

import zmq
from bson import BSON, Binary

from . import util

class SeerClient(object):
    __shared_state = { "initialized": False }

    def __init__(self):
        self.__dict__ = self.__shared_state
        if self.initialized: return
        self.initialized = True

        context = zmq.Context.instance()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect('ipc:///tmp/seer')

    def __call__(self, method, **args):
        req = dict(method=method, **args)
        b_req = BSON.from_dict(req)
        self.socket.send(b_req)
        b_res = self.socket.recv()
        res = BSON(b_res).to_dict()
        if res['status'] == 'ok': return res['res']
        print res['res']
        assert res['status'] == 'ok'

    def get_config(self, key):
        return self('get_config', key=key)

    def get_image(self, index, camera):
        return self('get_image', index=index, camera=camera)

    def reload_inspections(self, index, camera):
        return self('get_image', index=index, camera=camera)

class SeerService(object):

    def __init__(self, seer):
        self.seer = seer

    def start(self):
        thd = threading.Thread(target=self.run)
        thd.daemon = True
        thd.start()

    def run(self):
        context = zmq.Context.instance()
        socket = context.socket(zmq.REP)
        socket.bind('ipc:///tmp/seer')
        while True:
            req = socket.recv()
            res = self.handle(req)
            socket.send(res)

    def handle(self, req):
        try:
            req = BSON(req).to_dict()
            s_method = 'handle_' + req.pop('method')
            method = getattr(self, s_method)
            res = method(**req)
            res = dict(status='ok', res=res)
        except:
            res = dict(status='error', res=traceback.format_exc())
        return BSON.from_dict(res)

    def handle_get_config(self, key):
        return dict(value=getattr(self.seer.config, key))

    def handle_get_image(self, index, camera):
        try:
            f = util.get_seer().lastframes[index][camera]
            image = f.image.getPIL()
        except Exception, ex:
            print 'Error acquiring image (%r), substituting logo' % ex
            import SimpleCV
            image = SimpleCV.Image('logo').getPIL()
        s = StringIO()
        try:
            image.save(s, "webp", quality = 80)
            return dict(
                content_type='image/webp',
                data=Binary(s.getvalue()))
        except:
            image.save(s, "jpeg", quality = 80)
            return dict(
                content_type='image/jpeg',
                data=Binary(s.getvalue()))

    def handle_reload_inspections(self):
        self.seer.reloadInspections()
        return dict()
