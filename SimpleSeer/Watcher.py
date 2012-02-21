from base import *
from Session import Session

class Watcher(SimpleDoc):
    """
    The Watcher reviews results in SimpleSeer, and has two handler patterns:
      - self.conditions holds a list of conditions and parameters and returns a message pass or fail.
        
      - self.handlers are function references that receive all messages from the
        conditions.  They can be wired and must be a class method.  
    
    A typical watcher will have a sample size, and wil look in the SimpleSeer() to see
    the most recently recorded measurements.  It can check state on the entire system,
    and may potentially reference the Web, Control, and Display interfaces.  They
    also are responsible for recording any Results and Statistics.    
    
    
    w = Watcher(
        name = "Lid test",
        conditions = [
            {"method": "greater_than",
            "threshold": 100,
            "measurement": Measurement.objects[0].id,
            "label": "Object Too Large" }
        ],
        handlers = ["warning"])
    w.check()
    """
    name = mongoengine.StringField()
    conditions = mongoengine.ListField(mongoengine.DictField())
    handlers = mongoengine.ListField(mongoengine.StringField())#this might be a relation 
    
    
    def __repr__(self):
        return "<Watcher object '%s' conditions: %d, handlers: %s>" % (self.name, len(self.conditions), ", ".join(self.handlers))
    
    
    def check(self, results):
        """
        When the wather runs check, each of its conditions are checked.  If
        all conditions return Statistic objects, they are sent to each
        handler.
        """
        outcomes = []
        for condition in self.conditions:
            method_ref = getattr(self, condition["method"])
            condition = utf8convert(condition)
            outcomes.append(method_ref(results, **condition))
                
        for handler in self.handlers:
            function_ref = getattr(self, handler)
            function_ref(outcomes)
    
        return outcomes
    
    #conditions always have the first parameter as results
    #the rest are sent in from the watcher parameters
    #TODO, most of this stuff could move to a decorator
    #TODO these condition messages should be broken out into an object
    #TODO either weed out extra params or figure out an easy way to eliminate
    #the catchall
    def greater_than(self, results, **message):
        for r in results:
            if str(r.measurement) == str(message["measurement"]):
                message["passed"] = False
                if (r.numeric > message["threshold"]):
                    message['passed'] = True
                return message
        return
                    
    def less_than(self, results, **message):
        for r in results:
            if str(r.measurement) == str(message["measurement"]):
                message["passed"] = False
                if (r.numeric < message["threshold"]):
                    message['passed'] = True
                return message
        return
     
    def handler_passed(self, messages):
        for m in messages:
            if m and not m["passed"]:
                SimpleSeer.SimpleSeer().passed(False)
                return
            
        SimpleSeer.SimpleSeer().passed(True)
        #TODO, add a flag to record passes
    
    #warn if any fail
    def handler_warning(self, messages):
        for m in messages:
            if m and not m["passed"]:
                SimpleSeer.SimpleSeer().addWarning(m)
                #TODO, add a flag to record warnings
    
    #alert if any pass            
    def handler_fail(self, messages):
        for m in messages:
            if m and not m["passed"]:
                SimpleSeer.SimpleSeer().addFailure(m)
                #TODO, add a flag to record failures
    
import SimpleSeer