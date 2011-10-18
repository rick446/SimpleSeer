from base import *
from Session import Session
from Inspection import Inspection

class SimpleSeer(threading.Thread):
    """
    The SimpleSeer object 
    
    """
    __shared_state = { "initialized": False } 
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
            id = camerainfo['id']
            del camerainfo['id']
            self.cameras.append(Camera(id, camerainfo))
        #log initialized camera X
    
        Session().redis.set("cameras", json.dumps(self.config.cameras))
        #tell redis what cameras we have
        
        self.inspections = Inspection.m.find( enabled = 1 ).all()
        
        all_inspections = Inspection.m.find().all()
        Session().redis.set("inspections", all_inspections) 
         
        self.conditions = []
        #self.conditions = Events.m.find( { "enabled": 1 }).all()

        #self.display = Display()
        self.lastframes = []
        self.framecount = 0
        self.results = [] #results for each frame
        Session().redis.set("results", [])
        #NOTE THIS IS NOT CORRECT BEHAVIOR!
        #WE SHOULD GET FRAMES/RESULTS OUT OF REDIS
        
        #log display started

        #self.web = Web(self.config['web'])

        #self.controls = Controls(self.config['arduino'])
        
        self.initialized = True
        
        super(SimpleSeer, self).__init__()
        self.daemon = True
        
        if self.config.start_shell:
            self.shell_thread = Shell.ShellThread()
            self.shell_thread.start()

    def capture(self):
        count = 0
        currentframes = []
        for c in self.cameras:
            img = c.getImage()
            frame = Frame.make({"capturetime": time.time(), 
                "camera": self.config.cameras[count]['name']})
            frame.image = img
            
            if self.config.record_all:
                frame.m.save()
            
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
        frame_results = []
        for frame in frames:   
            for inspection in self.inspections:
                if frame.camera != inspection.camera:
                    continue
                
                results = inspection.execute(frame)
                if results:
                    frame_results.extend(results)
        
        self.results.append(frame_results)
        
    def check(self):
        for watcher in self.watchers:
            if watcher.enabled:
                watcher.check()
    
    def run(self):
        while True:
            timer_start = time.time()
            
            self.inspect()
            #self.check()
            
            count = 0
            for f in self.lastframes[-1]:
                jpgdata = StringIO()
                f.image.applyLayers().getPIL().save(jpgdata, "jpeg")
                Session().redis.set("currentframe_%d" % count, jpgdata.getvalue())
                Session().redis.set("histogram_%d" % count, f.image.histogram(20))
                count = count + 1
            
            #self.display.send(frames)
            
            timeleft = Session().poll_interval - (time.time() - timer_start)
            if timeleft > 0:
                time.sleep(timeleft)
            else:
                time.sleep(0)
    
    
    
from Frame import Frame
import Shell
