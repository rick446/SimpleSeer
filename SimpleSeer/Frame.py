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
    _image = mongoengine.BinaryField() #binary image data
    _layer = mongoengine.BinaryField(default = '') #layer data
    _imgcache = ''

    @apply
    def image():
        def fget(self):
            if self._imgcache != '':
                return self._imgcache
            
            bitmap = cv.CreateImageHeader((self.width, self.height), cv.IPL_DEPTH_8U, 3)
            cv.SetData(bitmap, self._image)
            
            self._imgcache = Image(bitmap)
            if self._layer:
                self._imgcache.dl()._mSurface = pygame.image.fromstring(self._layer, self._imgcache.size(), "RGBA")
            
            return self._imgcache
            
          
        def fset(self, img):
            self.width, self.height = img.size()
            self._image = img.getBitmap().tostring()
          
            if len(img._mLayers):
                if len(img._mLayers) > 1:
                    mergedlayer = DrawingLayer(img.size())
                    for layer in img._mLayers[::-1]:
                        layer.renderToOtherLayer(mergedlayer)
                else:
                    mergedlayer = img.dl()
                self._layer = pygame.image.tostring(mergedlayer._mSurface, "RGBA")
          
            self._imgcache = img
            
        return property(fget, fset)
       
    def __repr__(self):
       return "<SimpleSeer Frame Object %d,%d captured with '%s' at %s>" % (
            self.width, self.height, self.camera, self.capturetime.ctime()) 
        
    def save(self):
        if self._imgcache != '':
            self.image = self._imgcache #encode any layer changes made before save
            self._imgcache = ''

        super(Frame, self).save()
        
    @classmethod
    def capture(cls):
        return SimpleSeer.SimpleSeer().capture()
       
       
import SimpleSeer
