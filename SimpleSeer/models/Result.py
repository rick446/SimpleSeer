import mongoengine
import calendar

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

    def get_or_create_result(self):
        result, created =  Result.objects.get_or_create(
            auto_save=False, id=self.result_id)
        if created:
            result.numeric = self.numeric
            result.string = self.string
            result.inspection_id=self.inspection_id
            result.inspection_name = self.inspection_name
            result.measurement_id = self.measurement_id
            result.measurement_name = self.measurement_name
        return result, created

class Result(SimpleDoc, mongoengine.Document):
    """
    """
    #this needs some work yet, should be much simpler
    numeric = mongoengine.FloatField()
    #list = mongoEngine.ListField()  #todo encode results as lists or dicts
    string = mongoengine.StringField()
    capturetime = mongoengine.DateTimeField()
    camera = mongoengine.StringField()

    frame_id = mongoengine.ObjectIdField()

    inspection_id = mongoengine.ObjectIdField()
    inspection_name = mongoengine.StringField()
    measurement_id = mongoengine.ObjectIdField()
    measurement_name = mongoengine.StringField()
    
    meta = {
        'indexes': ["capturetime", ('camera', '-capturetime'), "frame", "inspection", "measurement"]
    }

    
    def capEpochMS(self):
        # Shortcut to return the capture time in epoch microseconds
        
        epochTime = calendar.timegm(self.capturetime.timetuple()) + self.capturetime.time().microsecond / 1000000.0
        # Quick hack for jim: may change this:
        # epochTime *= 1000
        return epochTime

    capturetimeEpochMS = property(capEpochMS)

    def save(self, *args, **kwargs):
        # Push notification to OLAP to decide whether to publish this update
        from .OLAP import RealtimeOLAP
        o = RealtimeOLAP()
        o.realtime(self)
        
        super(Result, self).save(*args, **kwargs)

