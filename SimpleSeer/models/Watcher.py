import mongoengine

from .base import SimpleDoc, SimpleEmbeddedDocument, WithPlugins
from .Measurement import Measurement
from .Alert import Alert

class Handler(SimpleEmbeddedDoc, mongoengine.EmbeddedDocument):
    name = mongoengine.StringField()
    args = mongoengine.DictField()

class Watcher(SimpleDoc, WithPlugins, mongoengine.Document):
    """
    The Watcher reviews results in SimpleSeer, and has two handler patterns:
      - self.condition holds a condition which, if failed, will prevent further processing
      - self.handlers are function references that will be called if the
    condition evaluates to True.
    
    A typical watcher will have a sample size, and wil look in the SimpleSeer() to see
    the most recently recorded measurements.  It can check state on the entire system,
    and may potentially reference the Web, Control, and Display interfaces.  They
    also are responsible for recording any Results and Statistics.    
    
    
    w = Watcher(
        name = "Stress test",
        condition = 'blob_angle > 70',
        handlers = ["warning"])
    w.check()
    """
    name = mongoengine.StringField()
    condition = mongoengine.StringField()
    handlers = mongoengine.ListField(mongoengine.EmbeddedDocumentField(Handler))
    handlers = mongoengine.ListField(mongoengine.StringField())#this might be a relation 

    def __repr__(self):
        return "<Watcher object '%s' conditions: %d, handlers: %s>" % (self.name, len(self.conditions), ", ".join(self.handlers))
    
    def check(self, results):
        # Create a dict of lists of results keyed by measurement name
        result_dict = {}
        for r in results:
            m = Measurement.objects.get(_id=r.measurement)
            lst = result_dict.setdefault(m.name, [])
            lst.append(r)
        user_namespace = dict(
            results=result_dict)
        # "promote" members of result_dict to user_namespace if they don't
        # conflict with things already in user_namespace
        for k, v in result_dict.items():
            user_namespace.setdefault(k, v)
        outcome = eval(self.condition, user_namespace)
        # If outcome is true, call handler on result set
        if outcome:
            for handler in self.handlers:
                function_ref = getattr(self, handler + '_handler', None)
                if function_ref is None:
                    function_ref = self.get_plugin(handler)
                function_ref(results)

    @classmethod
    def info_handler(cls, results, message='info'):
        Alert.info(message)

    @classmethod
    def warning_handler(cls, results, message='warning'):
        Alert.warning(message)

    @classmethod
    def error_handler(cls, results, message='error'):
        Alert.error(message)

        
