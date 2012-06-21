from cStringIO import StringIO

import mongoengine

from SimpleSeer.base import Image, pil, pygame
from SimpleSeer import util

from formencode import validators as fev
from formencode import schema as fes
import formencode as fe

from .base import SimpleDoc
from .FrameFeature import FrameFeature
from .Clip import Clip
from .Result import Result, ResultEmbed
from .. import realtime
from ..util import LazyProperty


class FrameSchema(fes.Schema):	
    camera = fev.UnicodeString(not_empty=True)
	#TODO, make this feasible as a formencode schema for upload




class Frame(SimpleDoc, mongoengine.Document):
    """
        Frame Objects are a mongo-friendly wrapper for SimpleCV image objects,
        containing additional properties for the originating camera and time of capture.

        Note that Frame.image property must be used as a getter-setter.

        >>> f = SimpleSeer.capture()[0]  #get a frame from the SimpleSeer module
        >>> f.image.dl().line((0,0),(100,100))
        >>> f.save()
        >>> 
    """
    capturetime = mongoengine.DateTimeField()
    camera = mongoengine.StringField()
    features = mongoengine.ListField(mongoengine.EmbeddedDocumentField(FrameFeature))
    results = mongoengine.ListField(mongoengine.EmbeddedDocumentField(ResultEmbed))
    #features     
    
    height = mongoengine.IntField(default = 0)
    width = mongoengine.IntField(default = 0)
    clip_id = mongoengine.ObjectIdField(default=None)
    clip_frame = mongoengine.IntField(default=None)
    imgfile = mongoengine.FileField()
    layerfile = mongoengine.FileField()
    thumbnail_file = mongoengine.FileField()
    _imgcache = ''

    meta = {
        'indexes': ["capturetime", ('camera', '-capturetime')]
    }

    @LazyProperty
    def thumbnail(self):
        if self.thumbnail_file.grid_id is None:
            img = self.image
            thumbnail_img = img.scale(140.0 / img.height)
            img_data = StringIO()
            thumbnail_img.save(img_data, "jpeg", quality = 25)
            self.thumbnail_file.put(img_data.getvalue(), content_type='image/jpeg')
        else:
            self.thumbnail_file.get().seek(0,0)
            thumbnail_img = Image(pil.open(StringIO(self.thumbnail_file.read())))
        return thumbnail_img

    @LazyProperty
    def clip(self):
        return Clip.objects.get(id=self.clip_id)

    @property
    def image(self):
        if self._imgcache != '':
            return self._imgcache
        if self.clip is not None:
            return self.clip.images[self.clip_frame]

        self.imgfile.get().seek(0,0) #hackity hack, make sure the FP is at 0
        if self.imgfile != None:
            try:
                self._imgcache = Image(pil.open(StringIO(self.imgfile.read())))
            except (IOError, TypeError): # pragma no cover
                self._imgcache = None
        else: # pragma no cover
            self._imgcache = None


        if self.layerfile:
            self.layerfile.get().seek(0,0)
            self._imgcache.dl()._mSurface = pygame.image.fromstring(self.layerfile.read(), self._imgcache.size(), "RGBA")

        return self._imgcache

    @image.setter
    def image(self, value):
        self.width, self.height = value.size()
        self._imgcache = value
       
    def __repr__(self): # pragma no cover
       return "<SimpleSeer Frame Object %d,%d captured with '%s' at %s>" % (
            self.width, self.height, self.camera, self.capturetime.ctime()) 
        
    def save(self, *args, **kwargs):
        #TODO: sometimes we want a frame with no image data, basically at this
        #point we're trusting that if that were the case we won't call .image
        realtime.ChannelManager().publish('frame.', self)

        if self._imgcache != '':
            s = StringIO()
            img = self._imgcache
            if self.clip_id is None:
                img.getPIL().save(s, "jpeg", quality = 100)
                self.imgfile.delete()
                self.imgfile.put(s.getvalue(), content_type = "image/jpg")
          
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
            #self._imgcache = ''

        super(Frame, self).save(*args, **kwargs)
        
        #TODO, this is sloppy -- we should handle this with cascading saves
        #or some other mechanism
        for r in self.results:
            result,created = Result.objects.get_or_create(auto_save=False, id=r.result_id)
            result.capturetime = self.capturetime
            result.camera = self.camera
            result.frame = self.id
            result.inspection = r.inspection_id
            result.measurement = r.measurement_id
            result.string = r.string
            result.numeric = r.numeric
            result.save(*args, **kwargs)
        
    def serialize(self):
        s = StringIO()
        try:
            self.image.save(s, "webp", quality = 80)
            return dict(
                content_type='image/webp',
                data=s.getvalue())
        except KeyError:
            self.image.save(s, "jpeg", quality = 80)
            return dict(
                content_type='image/jpeg',
                data=s.getvalue())

    @classmethod
    def search(cls, filters, sorts, skip, limit):
        db = cls._get_db()
        # Use the agg fmwk to generate frame ids
        pipeline = [
            # initial match to reduce number of frames to search
            {'$match': filters },
            # unwind features and results so we can do complex queries
            # against a *single* filter/result
            {'$unwind': '$features'},
            {'$unwind': '$results' },
            # Re-run the queries
            {'$match': filters },
            {'$sort': sorts },
            {'$project': {'_id': 1} }]
        cmd = db.command('aggregate', 'frame', pipeline=pipeline)
        total_frames = len(cmd['result'])
        seen = set()
        ids = []
        # We have to do skip/limit in Python so we can skip over duplicate frames
        for doc in cmd['result']:
            id = doc['_id']
            if id in seen: continue
            seen.add(id)
            if skip > 0:
                skip -= 1
                continue
            ids.append(id)
            if len(ids) >= limit: break
        frames = cls.objects.filter(id__in=ids)
        frame_index = dict(
            (f.id, f) for f in frames)
        chosen_frames = []
        for id in ids:
            frame = frame_index.get(id)
            if frame is None: continue
            chosen_frames.append(frame)
        return total_frames, chosen_frames
