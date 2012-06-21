from SimpleSeer import models as M
from SimpleSeer.plugins import base

"""

This simple plugin checks to see the time distance between two measurements

Example, show when a red object is seen after a face:

insp = Inspection( name= "face", method="face" ) 
insp.save()

meas = Measurement( name="facecolor", inspection = insp.id, method="meancolor")
meas.save()

meas = Measurement( name= "Time Since Last Face", method="timebetween", inspection = insp.id)
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
            insp2 = insp #we test time between measurements from the same inspection
                    
        results1 = M.Result.objects(inspection_id = insp2).order_by("-capturetime")
        if not len(results1):
            return []
            
        r1 = results1[0]
        r2param = dict(
          inspection_id = insp
        )
        if not showneg or insp == insp2:
            r2param["capturetime__lt"] = r1.capturetime
            
        results2 = M.Result.objects(**r2param).order_by("-capturetime")
        if not len(results2):
            return []
            
        r2 = results2[0]
        
        maxtime = max(r2.capturetime, r1.capturetime)
        if self.measurement.id:
            #TODO, we can check the SS.results array as well
            if len(M.Result.objects(measurement_id = self.measurement.id, capturetime__gte = maxtime)):
                return [] 
        
        if r1.capturetime > r2.capturetime:
          timediff = (r1.capturetime - r2.capturetime).seconds
        else:
          timediff = (r2.capturetime - r2.capturetime).seconds

        return [timediff]
