#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session

if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "../default.cfg"

Session(config_file)

from SimpleSeer.models.Inspection import Inspection
from SimpleSeer.models.Inspection import Measurement 
from SimpleSeer.models.OLAP import OLAP 
 

Inspection.objects.delete()
Measurement.objects.delete()
OLAP.objects.delete()


insp = Inspection( name= "Motion", method="motion")
insp.save()

meas = Measurement( name="movement", label="Movement", method = "movement", parameters = dict(), units = "", featurecriteria = dict( index = 0 ), inspection = insp.id )
meas.save()


omove = OLAP(name='MotionMovingAverage', queryInfo = dict( name = 'Motion' ), descInfo = dict( formula = 'moving', window = 3), chartInfo = dict ( name='line', color = 'blue', min = 0, max = 100))
omove.save()
oraw = OLAP(name='Motion', queryInfo = dict( name = 'Motion' ), descInfo = None, chartInfo = dict ( name='line', color = 'blue', min = 0, max = 100))
oraw.save()
