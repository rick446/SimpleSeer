from base import *
from Session import Session
from Inspection import Inspection
from Watcher import Watcher
from Web import *



class SimpleSeer(threading.Thread):
    """
    The SimpleSeer object 
    
    """
    __shared_state = { "initialized": False }
    web_interface = None
    halt = False
    plugins = {}
#    cameras = []
#    shell_thread = ''
#    display = ''
#    camera_on = 0
#    lastframes = []
#    config = {}
#    framecount = {}
#    warnings = []
#    alerts = []
#    passed = []

    def __init__(self):
        self.__dict__ = self.__shared_state
        #ActiveState "Borg" Singleton replacement design
        if self.initialized:
            return  #successive calls to SimpleSeer simply return the borg'd object

        #read config file
        self.config = Session()

        self.cameras = []
        
        #TODO, make this sensitive to module.__path__
        self.pluginpath = "./SimpleSeer/plugins"
        
        for camera in self.config.cameras:
            camerainfo = camera.copy()
            if camerainfo.has_key('virtual'):
                self.cameras.append(VirtualCamera(camerainfo['source'], camerainfo['virtual']))
            else:
                id = camerainfo['id']
                del camerainfo['id']
                if camerainfo.has_key('crop'):
                    del camerainfo['crop']
                self.cameras.append(Camera(id, camerainfo))
        #log initialized camera X
        self.init_logging()
        
        Session().redis.set("cameras", self.config.cameras)
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
        
        if self.config.start_shell:
            self.shell_thread = Shell.ShellThread()
            self.shell_thread.start()

        Frame.capture()
        Inspection.inspect()
        self.update()
        self.web_interface = Web()


    #i don't really like this too much -- it should really update on
    #an Inspection load/save

    def init_logging(self):
      # set up logging to file - see previous section for more details
      logging.basicConfig(level=logging.DEBUG,
                          format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                          datefmt='%m-%d %H:%M',
                          filename='seer.log',
                          filemode='w')
      # define a Handler which writes INFO messages or higher to the sys.stderr
      console = logging.StreamHandler()
      console.setLevel(logging.INFO)
      # set a format which is simpler for console use
      formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
      # tell the handler to use this format
      console.setFormatter(formatter)
      # add the handler to the root logger
      logging.getLogger('').addHandler(console)


    def log(self, param = None):
      if param:
        logging.debug(param)


    def clear(self):
        Inspection.objects.delete()
        Measurement.objects.delete()
        Watcher.objects.delete()
        Frame.objects.delete()
        self.lastframes = []
        Session().redis.flushdb()
        self.reloadInspections()
        

    def reloadInspections(self):
        i = list(Inspection.objects)
        Session().redis.set("inspections", i)
        m = list(Measurement.objects)
        Session().redis.set("measurements", m)
        w = list(Watcher.objects)
        #Session().redis.set("watchers", w) #TODO Fix encoding
        self.inspections = i
        self.measurements = m
        #self.watchers = w
        return i

    def loadPlugins(self):
        self.plugins = {}
        plugins = self.plugins

        
        for plugin in [ name for name in os.listdir(self.pluginpath) if os.path.isdir(os.path.join(self.pluginpath, name)) ]:
            try:
                plugins[plugin] = __import__("SimpleSeer.plugins."+plugin)
            except ImportError as e:
                warnings.warn(e)
                
        return self.plugins

    def loadImageSet(self, imgs = None):
        '''
        This function requires an SimpleCV image set to be passed in.

        >>> imgs = SimpleCV.ImageSet()
        >>> imgs.load('/path/to/dir')
        >>> SS.loadImageSet(imgs)
        '''

        if imgs is None:
          log("ImageSet cannot load: empty")
          return

        if not isinstance(imgs, SimpleCV.ImageSet):
          log("ImageSet needs SimpleCV imageSet passed")
          return

        
        for i in imgs:
            img = i
            frame = Frame(capturetime = datetime.now(), 
                camera = self.cameras[-1])
            frame.image = img
            
            if self.config.record_all:
                frame.save()
            
             
            while len(self.lastframes) > self.config.max_frames:
                self.lastframes.pop(0)
                            
            self.framecount = self.framecount + 1
            Session().redis.set("framecount", self.framecount)
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

      imgs = SimpleCV.ImageSet(path)
      self.loadImageSet(imgs)
      
        
    def capture(self):
        count = 0
        currentframes = []
        
        for c in self.cameras:
            img = c.getImage()
            if self.config.cameras[0].has_key('crop'):
                img = img.crop(*self.config.cameras[0]['crop'])
            frame = Frame(capturetime = datetime.now(), 
                camera= self.config.cameras[count]['name'])
            frame.image = img
            
            if self.config.record_all:
                frame.save()
            
            currentframes.append(frame)
            
            while len(self.lastframes) > self.config.max_frames:
                self.lastframes.pop(0)
                            
            self.framecount = self.framecount + 1
            Session().redis.set("framecount", self.framecount)
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
                    
            for watcher in list(Watcher.objects):
                watcher.check(frame.results)
                    
        return 
                
    def check(self):
        for watcher in self.watchers:
            if watcher.enabled:
                watcher.check()
                
    def update(self):
        
        count = 0
        for f in self.lastframes[-1]:
            jpgdata = StringIO()
            f.image.applyLayers().getPIL().save(jpgdata, "jpeg", quality = 95)
            Session().redis.setraw("currentframe_%d" % count, jpgdata.getvalue())
            Session().redis.set("histogram_%d" % count, f.image.histogram(50))
            Session().redis.set("currentframedata_%d" % count, f)
            Session().redis.set("results", self.results) #TODO, PUT A LIMIT (last 50 readings?  time?)
            count = count + 1
    
    def refresh(self):
        self.reloadInspections()
        self.inspect()
        self.update()
    
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
        while not self.halt:
            timer_start = time.time()
            self.inspect()
            
            if self.check():
                self.update(self)
            
            #self.display.send(frames)
            
            timeleft = Session().poll_interval - (time.time() - timer_start)
            if timeleft > 0:
                time.sleep(timeleft)
            else:
                time.sleep(0)
    
    #TODO, this doesn't work yet
    def stop(self):  #this should be called from an external thread
        self.halt = True
        cherrypy.engine.stop()
        self.join()
        
    def passed(self, state = None):
        if state == None:
            return Session().redis.get("passed")
        
        Session().redis.set("passed", state)
        return state
    
    def addWarning(self, warning):
        #self.passed(False)
        #TODO, move this to rpush/lrange
        warnjson = Session().redis.get("warnings")
        if warnjson:
            warnings = json.loads(warnjson)
        else:
            warnings = []
        warnings.append(warning)
        Session().redis.set("warnings", warnings)
        
    def addFail(self, failure):
        self.passed(False)
        #TODO, move this to rpush/lrange
        failurejson = Session().redis.get("failures")
        if failurejson:
            failures = json.loads(failurejson)
        else:
            failures = []
        
        failures.append(failure)
        Session().redis.set("failures", failures)

    
def log_wrapper(self, *arg, **kwargs):
  return SimpleSeer().log(*arg, **kwargs)


SimpleLog.__call__ = log_wrapper
from Frame import Frame
import Shell
