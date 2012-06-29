import glob
import gevent.queue
from datetime import datetime

import vpx
import bson
import numpy as np
from SimpleCV import Camera as ScvCamera
from SimpleCV import VirtualCamera, Kinect, FrameSource, Image, Scanner

from . import util
from . import models as M

class VideoCamera(object):

    def __init__(self, stillcam, rate,
                 frames_per_clip=10, deadline=vpx.VPX_DL_REALTIME,
                 queue_size=50):
        self._cam = stillcam
        self._rate = rate
        self._fpc = frames_per_clip
        self._deadline = deadline
        self._queue_size = queue_size
        self._gl = None
        # Create encoder
        img = self._cam.getImage()
        self.width, self.height = img.width, img.height
        self._encoder = M.Clip.encoder(
            self.width, self.height, rate,
            frames_per_clip=self._fpc,
            deadline=self._deadline)
        # Create clock & frame queue
        self.set_rate(rate)
        self._frame_queue = gevent.queue.Queue()

    def set_rate(self, rate_in_hz):
        self._rate = rate_in_hz
        self._clock = util.Clock(rate_in_hz, sleep=gevent.sleep)
        self._encoder = M.Clip.encoder(
            self.width, self.height, rate_in_hz,
            frames_per_clip=self._fpc,
            deadline=self._deadline)
        if self._gl:
            self.stop()
            self.start()

    def start(self):
        self._gl = gevent.spawn_link_exception(self.run)
        return self._gl

    def stop(self):
        self._gl.kill()

    def run(self):
        frames = gevent.queue.Queue()
        def images():
            while True:
                self._clock.tick()
                image = self._cam.getImage()
                frame = M.Frame(
                    capturetime=datetime.utcnow(),
                    camera=self._cam.name,
                    clip_id=bson.ObjectId() # fake, will replace
                    )
                frame.image = image
                frames.put(frame)
                while self._frame_queue.qsize() > self._queue_size:
                    print 'Dropped frame!'
                    self._frame_queue.get()
                self._frame_queue.put(frame)
                yield image
        for clip in self._encoder(images()):
            clip.save()
            for f_no in xrange(self._fpc):
                frame = frames.get()
                frame.clip_id = clip.id
                frame.clip_frame = f_no
                frame.clip = clip
                frame.save()
                gevent.sleep(0)

    def getFrame(self):
        return self._frame_queue.get()

class StillCamera(object):

    def __init__(self, name='default', crop=None, **cinfo):
        self.name = name
        self.crop = crop
        if 'virtual' in cinfo:
            cam = VirtualCamera(cinfo['source'], cinfo['virtual'])
        elif 'scanner' in cinfo:
            cinfo.pop('scanner')
            id = cinfo.pop('id')
            cam = Scanner(id, cinfo)
        elif 'directory' in cinfo:
            cam = DirectoryCamera(cinfo['directory'])
        elif 'kinect' in cinfo:
            cam = Kinect()
            cam._usedepth = 0
            cam._usematrix = 0
            if cinfo["kinect"] == "depth":
                cam._usedepth = 1
            elif cinfo["kinect"] == "matrix":
                cam._usematrix = 1
        else:
            cam = ScvCamera(cinfo['id'], prop_set=cinfo)
        self._scv_cam = cam

    def getImage(self):
        if isinstance(self._scv_cam, Kinect):
            if self._scv_cam._usedepth == 1:
                img = self._scv_cam.getDepth()
            elif self._scv_cam._usematrix == 1:
                mat = self._scv_cam.getDepthMatrix().transpose()
                img = Image(np.clip(mat - np.min(mat), 0, 255))
            else:
                img = self._scv_cam.getImage()
        else:
            img = self._scv_cam.getImage()
        if self.crop:
            img = img.crop(self.crop)
        return img

    def getFrame(self):
        frame = M.Frame(capaturetime=datetime.utcnow(), camera=self.name)
        frame.image = self.getImage()
        return frame

    def __getattr__(self, item):
        return getattr(self._scv_cam, item)

class DirectoryCamera(FrameSource):
    filelist = []
    counter = 0

    def __init__(self, path):
        self.filelist = glob(path)
        self.counter = 0

    def getImage(self):
        i = Image(self.filelist[self.counter])
        self.counter = (self.counter + 1) % len(self.filelist)
        return i
