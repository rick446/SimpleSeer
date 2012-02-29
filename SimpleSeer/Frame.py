from base import *
from Session import Session
from FrameFeature import FrameFeature

"""
    Frame Objects are a mongo-friendly wrapper for SimpleCV image objects,
    containing additional properties for the originating camera and time of capture.
    
    Note that Frame.image property must be used as a getter-setter.

    >>> f = SimpleSeer.capture()[0]  #get a frame from the SimpleSeer module
    >>> f.image.dl().line((0,0),(100,100))
    >>> f.save()
    >>> 
"""
class Frame(SimpleDoc):
    capturetime = mongoengine.DateTimeField()
    camera = mongoengine.StringField()
    features = mongoengine.ListField(mongoengine.EmbeddedDocumentField(FrameFeature))
    #features 
    
    
    height = mongoengine.IntField(default = 0)
    width = mongoengine.IntField(default = 0)
    imgfile = mongoengine.FileField()
    layerfile = mongoengine.FileField()
    _image = mongoengine.BinaryField() #binary image data
    _layer = mongoengine.BinaryField(default = '') #layer data
    _imgcache = ''
    results = [] #cache for result objects when frame is unsaved

    @apply
    #TODO add a clean method
    #TODO add a lossy image mode
    #TODO add thumbs
    def image():
        def fget(self):
            if self._imgcache != '':
                return self._imgcache
            
            self._imgcache = Image(pil.open(StringIO(self.imgfile.read())))
            
            if self.layerfile:
                self._imgcache.dl()._mSurface = pygame.image.fromstring(self.layerfile.read(), self._imgcache.size(), "RGBA")
            
            return self._imgcache
            
          
        def fset(self, img):
            self.width, self.height = img.size()
            
            s = StringIO()
            img.getPIL().save(s, "png", quality = 100)
            self.imgfile.delete()
            self.imgfile.put(s.getvalue())
          
            if len(img._mLayers):
                if len(img._mLayers) > 1:
                    mergedlayer = DrawingLayer(img.size())
                    for layer in img._mLayers[::-1]:
                        layer.renderToOtherLayer(mergedlayer)
                else:
                    mergedlayer = img.dl()
                self.layerfile.delete()
                self.layerfile.put(pygame.image.tostring(mergedlayer._mSurface, "RGBA"))
                #TODO, make layerfile a compressed object
          
            self._imgcache = img
            
        return property(fget, fset)
       
    def __repr__(self):
       return "<SimpleSeer Frame Object %d,%d captured with '%s' at %s>" % (
            self.width, self.height, self.camera, self.capturetime.ctime()) 
        
    def save(self):
        if self._imgcache != '':
            self.image = self._imgcache #encode any layer changes made before save
            self._imgcache = ''
        
        results = self.results
        self.results = []

        super(Frame, self).save()
        
        for r in results:
            if not r.frame:  
                r.frame = self.id
                r.save()  #TODO, check to make sure measurement/inspection are saved
        
    @classmethod
    def capture(cls):
        return SimpleSeer.SimpleSeer().capture()
       
       
import SimpleSeer
