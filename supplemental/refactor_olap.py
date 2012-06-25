#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session

if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "../default.cfg"

Session(config_file)

from SimpleSeer.models.Result import Result
from SimpleSeer.models.OLAP import OLAP
from SimpleSeer.models.Chart import Chart
from SimpleSeer.models.Inspection import Inspection
from SimpleSeer.models.Measurement import Measurement 

# Note this cleans out all old results 
Result.objects.delete()
Inspection.objects.delete()
Measurement.objects.delete()
OLAP.objects.delete()
Chart.objects.delete()


insp = Inspection( name= "Motion", method="motion")
insp.save()

meas = Measurement( name="movement", label="Movement", method = "movement", parameters = dict(), units = "", featurecriteria = dict( index = 0 ), inspection = insp.id )
meas.save()

o1 = OLAP()
o1.name = 'Motion'  
o1.maxLen = 1000 
o1.queryType = 'measurement_id' 
o1.queryId = meas.id 
o1.fields = ['capturetime','numeric', 'measurement_id', 'inspection_id', 'frame_id']
o1.since = None
o1.before = None
o1.customFilter = {} 
o1.statsInfo = []
o1.save()

c1 = Chart()
c1.name = 'Motion'
c1.olap = o1.name
c1.style = 'column'
c1.minval = 0
c1.maxval = 100
c1.xtype = 'linear'
c1.colormap = {}
c1.labelmap = {}
c1.accumulate = False
c1.renderorder = 1
c1.halfsize = False
c1.realtime = True
c1.dataMap = ['capturetime','numeric']
c1.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c1.save()

o2 = OLAP()
o2.name = 'Motion, mean by minute'  
o2.maxLen = 1000 
o2.queryType = 'measurement_id' 
o2.queryId = meas.id
o2.groupTime = 'minute' 
o2.fields = ['capturetime','numeric', 'measurement_id', 'inspection_id', 'frame_id']
o2.since = None
o2.before = None
o2.customFilter = {} 
o2.statsInfo = [{'avg':'numeric'}]
o2.save()

c2 = Chart()
c2.name = 'Motion, mean by minute'
c2.olap = o2.name
c2.style = 'column'
c2.minval = 0
c2.maxval = 100
c2.xtype = 'linear'
c2.colormap = {}
c2.labelmap = {}
c2.accumulate = False
c2.renderorder = 1
c2.halfsize = False
c2.realtime = True
c2.dataMap = ['capturetime','numeric']
c2.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c2.save()
