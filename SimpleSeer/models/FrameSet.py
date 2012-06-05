from copy import deepcopy

import mongoengine
from formencode import validators as fev
from formencode import schema as fes
import formencode as fe


from SimpleSeer import validators as V
from SimpleSeer import util


from .base import SimpleDoc, WithPlugins
from .Measurement import Measurement
from .FrameFeature import FrameFeature


class FrameSetSchema(fes.Schema):
    name = fev.UnicodeString(not_empty=True)
    frames = V.JSON(if_empty=dict, if_missing=None)
    #parent = V.ObjectId(if_empty=None, if_missing=None)
    #method = fev.UnicodeString(not_empty=True)
    #camera = fev.UnicodeString(if_empty="")
    #parameters = V.JSON(if_empty=dict, if_missing=None)
    #filters = V.JSON(if_empty=dict, if_missing=None)
    #richattributes = V.JSON(if_empty=dict, if_missing=None)
    #morphs = fe.ForEach(fev.UnicodeString(), convert_to_list=True)



class FrameSet(SimpleDoc, WithPlugins, mongoengine.Document):
    name = mongoengine.StringField()
    frames = mongoengine.ReferenceField('Frame')

    def __repr__(self):
      return "[%s Object <%s> ]" % (self.__class__.__name__, self.name)
