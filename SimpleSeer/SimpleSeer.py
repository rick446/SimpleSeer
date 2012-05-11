import os
import gc
import time
import logging
import warnings
import threading
from datetime import datetime

import pkg_resources

from . import models as M
from .Session import Session

from SimpleCV import Camera, VirtualCamera, Kinect, FrameSource
from SimpleCV import ImageSet, Image
import numpy as np
from glob import glob

log = logging.getLogger(__name__)

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


class SimpleSeer(object):
    """
    The SimpleSeer object 
    
    """
    __shared_state = { "initialized": False }
    web_interface = None
    halt = False
    plugins = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        #ActiveState "Borg" Singleton replacement design
        if self.initialized:
            return  #successive calls to SimpleSeer simply return the borg'd object

        #read config file
        self.config = Session()

        self.cameras = []
       
        for camera in self.config.cameras:
            camerainfo = camera.copy()

            if camerainfo.has_key('virtual'):
                self.cameras.append(VirtualCamera(camerainfo['source'], camerainfo['virtual']))
            elif camerainfo.has_key('directory'):
                self.cameras.append(DirectoryCamera(camerainfo['directory']))
            elif camerainfo.has_key('kinect'):
                k = Kinect()
                k._usedepth = 0
                k._usematrix = 0
                if camerainfo["kinect"] == "depth":
                    k._usedepth = 1
                elif camerainfo["kinect"] == "matrix":
                    k._usematrix = 1
                
                self.cameras.append(k)
            else:
                id = camerainfo['id']
                del camerainfo['id']
                if camerainfo.has_key('crop'):
                    del camerainfo['crop']
                self.cameras.append(Camera(id, camerainfo))
        #log initialized camera X
        
        #Session().redis.set("cameras", self.config.cameras)
        #tell redis what cameras we have
        
        self.reloadInspections() #initialize inspections so they get saved to redis
         
        self.loadPlugins()
        self.lastframes = []
        self.framecount = 0
        
        #log display started

        #self.controls = Controls(self.config['arduino'])
        
        self.initialized = True
        
        super(SimpleSeer, self).__init__()
        self.daemon = True
        
        M.Frame.capture()
        #~ Inspection.inspect()
        #self.update()
        if self.config.auto_start:
            self.start()
        self.connection_file = None

    #i don't really like this too much -- it should really update on
    #an Inspection load/save

#    def clear(self):
#        Inspection.objects.delete()
#        Measurement.objects.delete()
#        Watcher.objects.delete()
#        Frame.objects.delete()
#        self.lastframes = []
#        Session().redis.flushdb()
#        self.reloadInspections()
        

    def reloadInspections(self):
        i = list(M.Inspection.objects)
#        Session().redis.set("inspections", i)
        m = list(M.Measurement.objects)
#        Session().redis.set("measurements", m)
        w = list(M.Watcher.objects)
#        Session().redis.set("watchers", w) #TODO Fix encoding
        self.inspections = i
        self.measurements = m
        self.watchers = w

    def loadPlugins(self):
        plugin_types = dict(
            inspection=M.Inspection,
            measurement=M.Measurement,
            watcher=M.Watcher)
        for ptype, cls in plugin_types.items():
            for ep in pkg_resources.iter_entry_points('seer.plugins.' + ptype):
                log.info('Loading %s plugin %s', ptype, ep.name)
                try:
                    cls.register_plugin(ep.name, ep.load())
                except Exception, err:
                    log.error('Failed to load %s plugin %s: %s', ptype, ep.name, err)

    def loadImageSet(self, imgs = None):
        '''
        This function requires an SimpleCV image set to be passed in.

        >>> imgs = SimpleCV.ImageSet()
        >>> imgs.load('/path/to/dir')
        >>> SS.loadImageSet(imgs)
        '''

        if imgs is None:
          log.info("ImageSet cannot load: empty")
          return

        if not isinstance(imgs, ImageSet):
          log.info("ImageSet needs SimpleCV imageSet passed")
          return

        
        for i in imgs:
            img = i
            frame = M.Frame(capturetime = datetime.now(), 
                camera = self.cameras[-1])
            frame.image = img            
             
            while len(self.lastframes) > self.config.max_frames:
                self.lastframes.pop(0)
                            
            self.framecount = self.framecount + 1
#            Session().redis.set("framecount", self.framecount)
            self.lastframes.append(frame)

    def loadImageDirectory(self, path = None):
      '''
      This function takes in a directory path of images to load
      into seer.  It then converts them into SimpleSeer frames.

      To use:
      >>> ss = SimpleSeer()
      >>> ss.loadImageDirectory('/path/to/imgs/')
      >>> ss.lastframes
      >>> ss.lastframes[-1].image.show()

      '''

      imgs = ImageSet(path)
      self.loadImageSet(imgs)
      
        
    def capture(self):
        gc.collect()
        count = 0
        currentframes = []
        self.framecount = self.framecount + 1

        for c in self.cameras:
            img = ""
            if c.__class__.__name__ == "Kinect" and c._usedepth == 1: 
                img = c.getDepth()
            elif c.__class__.__name__ == "Kinect" and c._usematrix == 1:
                mat = c.getDepthMatrix().transpose()
                img = Image(np.clip(mat - np.min(mat), 0, 255))
            else:
                img = c.getImage()
            if self.config.cameras[0].has_key('crop'):
                img = img.crop(*self.config.cameras[0]['crop'])
            frame = M.Frame(capturetime = datetime.utcnow(), 
                camera= self.config.cameras[count]['name'])
            frame.image = img
            currentframes.append(frame)
            
            while len(self.lastframes) > self.config.max_frames:
                self.lastframes.pop(0)
            # log.info('framecount is %s', len(self.lastframes))
                            
#            Session().redis.set("framecount", self.framecount)
            count = count + 1
            
                    
        self.lastframes.append(currentframes)            
            
        return currentframes
            
    def inspect(self, frames = []):
        if not len(frames) and not len(self.lastframes):
            frames = self.capture()
        elif not len(frames):
            frames = self.lastframes[-1]
        
        for frame in frames:
            frame.features = []
            frame.results = []
            for inspection in self.inspections:
                if inspection.parent:  #root parents only
                    continue
                
                if frame.camera != inspection.camera: #this camera only
                    continue
                
                results = inspection.execute(frame.image)
                frame.features.extend(results)
                for m in inspection.measurements:
                    frame.results += m.execute(frame, results)
                    
            for watcher in self.watchers:
                watcher.check(frame.results)
                    
        return 

    def frame(self, index = 0):
        if len(self.lastframes):    
            return self.lastframes[-1][index]
        else:
            frames = M.Frame.objects.order_by("-capturetime").skip(index)
            if len(frames):
                return frames[0]
            else:
                return None
        
    def check(self):
        for watcher in self.watchers:
            if watcher.enabled:
                watcher.check()

    def get_last_frame_ids(self):
        return [ [ f.id for f in frames ]
                 for frames in self.lastframes ]

    def get_frame_id(self, index, camera):
        return self.lastframes[index][camera].id
                
    def get_image(self, index, camera):
        frame = self.lastframes[index][camera]
        return frame.serialize()

#    def update(self):
        
#        count = 0
#        batch = { "histogram": [], "frame": [] }
#        for f in self.lastframes[-1]:
#            hist = f.image.histogram(50)
#            Session().redis.set("histogram_%d" % count, hist)
#            batch["histogram"].append(hist)
#            Session().redis.set("currentframedata_%d" % count, f)
#            batch["frame"].append(f)
#            count = count + 1

#        Session().redis.set("results", self.results) #TODO, PUT A LIMIT (last 50 readings?  time?)
#        batch["results"] = self.results
#        Session().redis.set("framecount", self.framecount)
#        Session().redis.set("batchframe", batch)
        #TODO add passes and failures to the batch
    
#    def refresh(self):
#        self.reloadInspections()
#        self.inspect()
#        self.update()
    
    @property
    def results(self):
        ret = []
        for frameset in self.lastframes:
            results = []
            for f in frameset:
                results += [f.results for f in frameset]
            
            ret.append(results)
            
        return ret
    
    def run(self):
        while True:
            time.sleep(0)
            while not self.halt:
                timer_start = time.time()
                self.capture()
                self.inspect()
                self.check()
                if self.config.record_all:
                    for frame in self.lastframes[-1]:
                        frame.save(safe = False)

                
                timeleft = Session().poll_interval - (time.time() - timer_start)

                if timeleft > 0:
                    time.sleep(timeleft)
                else:
                    time.sleep(0)
            time.sleep(0.1)

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
    
    #TODO, this doesn't work yet
    def stop(self):  #this should be called from an external thread
        self.halt = True
        
    def resume(self):
        self.halt = False
