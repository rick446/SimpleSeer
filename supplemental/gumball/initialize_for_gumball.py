#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session

if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "gumball.cfg"

Session(config_file)

from SimpleSeer.models import Result, Inspection, Measurement, Frame
from SimpleSeer.models.OLAP import OLAP, OLAPFactory
 

Frame.objects.delete()
Inspection.objects.delete()
Measurement.objects.delete()
OLAP.objects.delete()
Result.objects.delete()

insp = Inspection( name= "Region", 
  method="region", 
  parameters = { "x": 100, "y": 100, "w": 440, "h": 280 }, 
   camera='Color Check')
insp.save()

meas = Measurement( name="Gumball Color", label="Color", method = "closestcolor", inspection = insp.id )
meas.save()

insp2 = Inspection( name= "Delivery Confirmation",
  method="blob",
  parameters = { "thresh": 10, "limit": 1 },
  camera = "Delivery Check")
insp2.save()

meas2 = Measurement( name="Delivery Color", label="Color", method = "closestcolor", inspection = insp2.id )
meas.save()

meas3 = Measurement( name="Delivery Time", label="Seconds", method = "timebetween", inspection = insp2.id, 
  parameters = dict( inspection = insp.id ))
meas3.save()

meas4 = Measurement( name="Delivery Radius", label="radius", method = "radius")
meas4.save()


of = OLAPFactory()

qi = {'objType':'inspection', 'objId':insp2.id, 'objFields':['string', 'capturetimeEpochMS', 'inspection', 'frame', 'measurement', 'id'], 'round': [None, None, None, None, None, None], 'since':None, 'before':None, 'limit':1000, 'required':None}
cihist = {'name':'sumbucket', 'color':'blue', 'minval':0, 'xtype':'linear', 'ticker':10}
oraw = of.makeOLAP(queryInfo = qi, descInfo = None, chartInfo = cihist)
oraw.allow = 1000
oraw.name = 'ColorDelivery'
oraw.realtime = 1
oraw.save()
