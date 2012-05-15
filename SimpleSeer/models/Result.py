import mongoengine

from .base import SimpleDoc
from .. import realtime

class Result(SimpleDoc, mongoengine.Document):
    """
    """
    #this needs some work yet, should be much simpler
    numeric = mongoengine.FloatField()
    #list = mongoEngine.ListField()  #todo encode results as lists or dicts
    string = mongoengine.StringField()
    capturetime = mongoengine.DateTimeField()
    camera = mongoengine.StringField()

    inspection = mongoengine.ObjectIdField()
    frame = mongoengine.ObjectIdField()
    measurement = mongoengine.ObjectIdField()
    
    meta = {
        'indexes': ["capturetime", ('camera', '-capturetime'), "frame", "inspection", "measurement"]
    }

    def save(self, *args, **kwargs):
        realtime.ChannelManager().publish('frame', dict(
                string=self.string, object=self))
        super(Result, self).save(*args, **kwargs)
