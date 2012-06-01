import mongoengine

from .base import SimpleDoc, WithPlugins
from ..realtime import ChannelManager

class Alert(SimpleDoc, WithPlugins, mongoengine.Document):
    severity = mongoengine.StringField(max_length=1, choices=[
            ('I', 'Info'),
            ('W', 'Warning'),
            ('E', 'Error')])
    message = mongoengine.StringField()
    
    def __repr__(self):
        return "<Alert severity=%s message=%s>" % (
            self.severity, self.message)

    @classmethod
    def info(cls, message):
        ChannelManager().publish('alert/', dict(severity='info', message=message))
        return cls(severity='I', message=message)

    @classmethod
    def warn(cls, message):
        ChannelManager().publish('alert/', dict(severity='warn', message=message))
        return cls(severity='W', message=message)

    @classmethod
    def error(cls, message):
        ChannelManager().publish('alert/', dict(severity='error', message=message))
        return cls(severity='E', message=message)

    
