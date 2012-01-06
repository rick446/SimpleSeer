from base import *
from Session import Session
from Inspection import Inspection
from Web import *


class SimpleSeer(threading.Thread):
    """
    The SimpleSeer object 
    
    """
    __shared_state = { "initialized": False }
    web_interface = None
    halt = False
#    cameras = []
#    shell_thread = ''
#    display = ''
#    camera_on = 0
#    lastframes = []
#    config = {}
#    framecount = {}

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
                self.cameras.append(VirtualCamera(camerainfo['source'], camerainfo["virtual"]))
            else:
                id = camerainfo['id']
                del camerainfo['id']
                if camerainfo.has_key('crop'):
                    del camerainfo['crop']
                self.cameras.append(Camera(id, camerainfo))
                #log initialized camera X
    
        Session().redis.set("cameras", json.dumps(self.config.cameras))
        #tell redis what cameras we have
        
        self.inspections = Inspection.objects#all root level inspections
        
        Session().redis.set("inspections", self.inspections) 
         
        
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


        self.web_interface = Web()


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
                self.results.pop(0)
                            
            self.framecount = self.framecount + 1
            Session().redis.set("framecount", self.framecount)
            count = count + 1
            
                    
        self.lastframes.append(currentframes)            
            
        return currentframes
            
    def inspect(self):
        frames = self.capture()
        for frame in frames:   
            for inspection in self.inspections:
                if inspection.parent:  #root parents only
                    continue
                
                if frame.camera != inspection.camera: #this camera only
                    continue
                
                results = inspection.execute(frame.image)
                frame.features.extend(results)
        return frames
                
    def check(self):
        for watcher in self.watchers:
            if watcher.enabled:
                watcher.check()
                
    def update(self):
        
        count = 0
        for f in self.lastframes[-1]:
            jpgdata = StringIO()
            f.image.applyLayers().getPIL().save(jpgdata, "jpeg", quality = 95)
            Session().redis.set("currentframe_%d" % count, jpgdata.getvalue())
            Session().redis.set("histogram_%d" % count, f.image.histogram(20))
            Session().redis.set("currentframedata_%d" % count, f)
            count = count + 1
    
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
        
    
    
from Frame import Frame
import Shell
