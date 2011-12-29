
from base import *
from Session import Session
from Measurement import Measurement
from Inspection import Inspection
from Frame import Frame


class Result(SimpleDoc):
    """
    Result( {
       "data": ["1","2","3"]
    
    """
    #this needs some work yet, should be much simpler
    data = mongoengine.ListField(mongoengine.StringField())
    roi = mongoengine.ListField(mongoengine.IntField())
    capturetime = mongoengine.FloatField()
    camera = mongoengine.StringField()
    is_numeric = mongoengine.IntField()

    measurement = mongoengine.ReferenceField(Measurement)
    inspection = mongoengine.ReferenceField(Inspection)
    frame = mongoengine.ReferenceField(Frame)
    
    @property
    def float_data(self):
        if not self.is_numeric:
            return None
        np.cast[float](self.data)
        
    @property
    def int_data(self):
        if not self.is_numeric:
            return None
        np.cast[int](self.data)
        
        
