from copy import deepcopy

import mongoengine
from formencode import validators as fev
from formencode import schema as fes
import formencode as fe


from SimpleSeer import validators as V
from SimpleSeer import util


from .base import SimpleDoc, WithPlugins
#from .Measurement import Measurement
#from .FrameFeature import FrameFeature
from .Frame import Frame


class FrameSetSchema(fes.Schema):
    name = fev.UnicodeString(not_empty=True)
    frames = fe.ForEach(fev.UnicodeString(), convert_to_list=True)

class FrameSet(SimpleDoc, WithPlugins, mongoengine.Document):
    name = mongoengine.StringField()
    #frames = mongoengine.ListField(mongoengine.ReferenceField('Frame'))
    frames = mongoengine.ListField(mongoengine.StringField())

    def __repr__(self):
      return "[%s Object <%s> ]" % (self.__class__.__name__, self.name)
