import mongoengine

from .base import SimpleDoc, SimpleEmbeddedDoc

class ResultEmbed(SimpleEmbeddedDoc, mongoengine.EmbeddedDocument):
    _jsonignore = ('result_id', 'inspection_id', 'measurement_id')
    result_id = mongoengine.ObjectIdField()
    numeric = mongoengine.FloatField()
    string = mongoengine.StringField()
    inspection_id = mongoengine.ObjectIdField()
    inspection_name = mongoengine.StringField()
    measurement_id = mongoengine.ObjectIdField()
    measurement_name = mongoengine.StringField()

    def __repr__(self):
        return '<ResultEmbed %s:%s = (%s,%s)>' % (
            self.inspection_name, self.measurement_name,
            self.numeric, self.string)

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
        # Push notification to OLAP to decide whether to publish this update
        from .OLAP import RealtimeOLAP
        o = RealtimeOLAP()
        o.realtime(self)
        
        super(Result, self).save(*args, **kwargs)

