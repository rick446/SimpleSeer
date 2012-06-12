from SimpleSeer import models as M
from SimpleSeer.plugins import base

"""

This simple plugin checks to see the time distance between two measurements

Example, show when a red object is seen after a face:

insp = Inspection( name= "face", method="face" ) 
insp.save()

insp2 = Inspection( name= "red object", method="blob", parameters=dict(
  thresh = 20, color = (255,0,0)
) ) 
insp2.save() 

meas = Measurement( name= "Time Since", method="timebetween", inspection = insp.id,
parameters=dict( since = insp2.id )
  
)
meas.save()

"""

class TimeBetweenMeasurement(base.MeasurementPlugin):

    def __call__(self, frame, features):
        
        params = self.measurement.parameters
        
        insp = self.measurement.inspection
        
        showneg = True
        if "since" in params:  #only show when insp2 is before insp1
            insp2 = params["since"]
            showneg = False
        elif "until" in params:
            insp2 = insp
            insp = params["until"]
            showneg = False
        elif "between" in params:
            insp = params["between"]
        else:
            print "you must provide since, between, or until as parameters"
            return []
                    
        results1 = Results.objects(inspection = insp2).order_by("-capturetime")
        if not len(results1):
            return []
            
        r1 = results1[0]
        r2param = dict(
          inspection = insp
        )
        if not showneg:
            r2param["capturetime__lt"] = r1.capturetime
            
        results2 = Results.objects(**r2param).order_by("-capturetime")
        if not len(results2):
            return []
            
        r2 = results2[0]
        
        maxtime = max(r2.capturetime, r1.capturetime)
        if self.measurement.id:
            #TODO, we can check the SS.results array as well
            if len(Result.objects(measurement = self.measurement.id, capturetime__gte = maxtime)):
                return [] 
        
        timediff = r1.capturetime - r2.capturetime

        return [timediff]
