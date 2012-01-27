
from base import *
from Session import Session
from Measurement import Measurement
from Inspection import Inspection
from Frame import Frame


class Result(SimpleDoc):
    """
    """
    #this needs some work yet, should be much simpler
    numeric = mongoengine.FloatField()
    string = mongoengine.StringField()
    capturetime = mongoengine.DateTimeField()
    camera = mongoengine.StringField()

    inspection = mongoengine.ObjectIdField()
    frame = mongoengine.ObjectIdField()
    measurement = mongoengine.ObjectIdField()
