#!/usr/bin/env python

from SimpleSeer.base import *
from SimpleSeer.Session import Session
from os import system
import mongoengine

system('echo "db.dropDatabase()" | mongo default')


if (len(sys.argv) > 1):
   config_file = sys.argv[1] 
else:
   config_file = "gumball.cfg"

Session(config_file)

from SimpleSeer.models import Inspection, Measurement, Frame, OLAP, Result, Chart
from SimpleSeer.models import Result, Inspection, Measurement, Frame



insp = Inspection( name= "Region", 
  method="region", 
  parameters = { "x": 100, "y": 100, "w": 440, "h": 280 })
   
insp.save()

meas = Measurement( name="Gumball Color", label="Color", method = "closestcolor", inspection = insp.id, 
parameters =  {u'ignore': {u'empty': [52.05419642857143,
   55.84642045454545,
   56.93068993506493],
  u'grey': [9.491712662337662, 12.480714285714285, 24.281233766233765]},
 u'pallette': {u'green': [183.29511363636362,
   191.0861038961039,
   33.63636363636363],
  u'orange': [253.12191558441558, 120.15337662337663, 11.212978896103897],
  u'purple': [129.46625, 80.79396103896104, 90.85826298701299],
  u'red': [254.67767045454545, 14.35101461038961, 27.175430194805195],
  u'yellow': [221.99814123376623, 174.07620941558443, 0.006461038961038961]}}
)
meas.save()

meas1 = Measurement( name="Delivery Color", label="Color", method = "closestcolor_manual", inspection = insp.id )
meas1.save()

meas3 = Measurement( name="Delivery Time", label="Seconds", method = "timebetween_manual", inspection = insp.id, 
  parameters = dict( inspection = insp.id ))
meas3.save()

meas4 = Measurement ( name="Delivery Count", label="Count", method = "countbetween_manual", inspection = insp.id)
meas4.save()



## Count before delivery
o0 = OLAP()
o0.name = 'DeliveryCount'  
o0.maxLen = 1000 
o0.queryType = 'measurement_id' 
o0.queryId = meas4.id 
o0.fields = ['capturetime','numeric', 'string', 'measurement_id', 'inspection_id', 'frame_id']
o0.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'field': 'string', 'default': 5}
o0.since = None
o0.before = None
o0.customFilter = {} 
o0.statsInfo = []
o0.notNull = 0
o0.save()

c0 = Chart()
c0.name = 'Candies Analyzed'
c0.description = 'How many candies were analyzed per selection.'
c0.olap = o0.name
c0.style = 'line'
c0.color = '#777'
c0.minval = 0
c0.maxval = None
c0.xtype = None
c0.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c0.labelmap = {}
c0.xTitle = 'Button Press'
c0.yTitle = 'Count'
c0.accumulate = False
c0.renderorder = 10
c0.halfsize = False
c0.realtime = True
c0.dataMap = ['capturetime','numeric']
c0.metaMap = ['string', 'measurement_id', 'inspection_id', 'frame_id']
c0.save()


"""
## Histogram of color of gumballs evaluated
o1 = OLAP()
o1.name = 'EvaledColor'  
o1.maxLen = 1000 
o1.queryType = 'measurement_id' 
o1.queryId = meas.id 
o1.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o1.since = None
o1.before = None
o1.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'field': 'string', 'default': 5}
o1.customFilter = {} 
o1.statsInfo = []
o1.save()

c1 = Chart()
c1.name = 'Color Evaluated'
c1.olap = o1.name
c1.style = 'column'
c1.minval = 0
c1.maxval = None
c1.xtype = 'linear'
c1.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c1.labelmap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c1.accumulate = True
c1.renderorder = 2
c1.halfsize = True
c1.realtime = True
c1.dataMap = ['capturetime','string']
c1.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c1.save()
"""

## Histogram of color of gumballs delivered
o2 = OLAP()
o2.name = 'DeliveredColor'  
o2.maxLen = 1000 
o2.queryType = 'measurement_id' 
o2.queryId = meas1.id 
o2.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o2.since = None
o2.before = None
o2.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'field': 'string', 'default': 5}
o2.customFilter = {} 
o2.statsInfo = []
o2.save()

c2 = Chart()
c2.name = 'Color Delivered'
c2.description = 'The number of times a selected color was delivered.'
c2.olap = o2.name
c2.style = 'column'
c2.minval = 0
c2.maxval = None
c2.color = '#777'
c2.xtype = 'linear'
c2.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c2.labelmap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c2.xTitle = 'Candy Color'
c2.yTitle = 'Count'
c2.useLabels = True
c2.accumulate = True
c2.renderorder = 3
c2.halfsize = False
c2.realtime = True
c2.dataMap = ['capturetime','string']
c2.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c2.save()

"""
## Delivery time
o3 = OLAP()
o3.name = 'DeliveryTime'  
o3.maxLen = 1000 
o3.queryType = 'measurement_id' 
o3.queryId = meas3.id 
o3.fields = ['capturetime','numeric', 'measurement_id', 'inspection_id', 'frame_id']
o3.since = None
o3.before = None
o3.customFilter = {} 
o3.statsInfo = []
o3.notNull = 0
o3.save()

c3 = Chart()
c3.name = 'Delivery Time'
c3.olap = o3.name
c3.style = 'spline'
c3.minval = 0
c3.maxval = None
c3.xtype = 'datetime'
c3.colormap = None
c3.labelmap = None
c3.accumulate = False
c3.renderorder = 100
c3.halfsize = False
c3.realtime = True
c3.dataMap = ['capturetime','numeric']
c3.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c3.save()
"""
"""
## Yellow gumball evaled
o4 = OLAP()
o4.name = 'DeliveredYellow'  
o4.maxLen = 1000 
o4.queryType = 'measurement_id' 
o4.queryId = meas.id 
o4.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o4.since = None
o4.before = None
o4.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'default':5, 'field': 'string'}
o4.customFilter = {'field': 'string', 'val': 'yellow'} 
o4.statsInfo = []
o4.postProc = {'movingCount':'string'}
o4.notNull = 0
o4.save()

c4 = Chart()
c4.name = 'Candies'
c4.olap = o4.name
c4.style = 'area'
c4.minval = 0
c4.maxval = None
c4.xtype = 'datetime'
c4.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c4.color = 'yellow'
c4.labelmap = {}
c4.accumulate = False
c4.renderorder = 4
c4.halfsize = False
c4.realtime = True
c4.dataMap = ['capturetime','string']
c4.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c4.save()

## Green gumball evaled
o5 = OLAP()
o5.name = 'DeliveredGreen'  
o5.maxLen = 1000 
o5.queryType = 'measurement_id' 
o5.queryId = meas.id 
o5.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o5.since = None
o5.before = None
o5.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'default':5, 'field': 'string'}
o5.customFilter = {'field': 'string', 'val': 'green'} 
o5.statsInfo = []
o5.postProc = {'movingCount':'string'}
o5.notNull = 0
o5.save()

c5 = Chart()
c5.name = 'Candies by Color Green'
c5.olap = o5.name
c5.chartid = c4.id
c5.style = 'area'
c5.minval = 0
c5.maxval = None
c5.xtype = 'datetime'
c5.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c5.color = 'green'
c5.labelmap = {}
c5.accumulate = False
c5.renderorder = c4.renderorder + 1
c5.halfsize = False
c5.realtime = True
c5.dataMap = ['capturetime','string']
c5.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c5.save()

## Purple gumball evaled
o6 = OLAP()
o6.name = 'DeliveredPurple'  
o6.maxLen = 1000 
o6.queryType = 'measurement_id' 
o6.queryId = meas.id 
o6.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o6.since = None
o6.before = None
o6.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'default':5, 'field': 'string'}
o6.customFilter = {'field': 'string', 'val': 'purple'} 
o6.statsInfo = []
o6.postProc = {'movingCount':'string'}
o6.notNull = 0
o6.save()

c6 = Chart()
c6.name = 'Candies by Color Purple'
c6.olap = o6.name
c6.chartid = c4.id
c6.style = 'area'
c6.minval = 0
c6.maxval = None
c6.xtype = 'datetime'
c6.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c6.color = 'purple'
c6.labelmap = {}
c6.accumulate = False
c6.renderorder = c4.renderorder + 1
c6.halfsize = False
c6.realtime = True
c6.dataMap = ['capturetime','string']
c6.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c6.save()


## Orange gumball evaled
o7 = OLAP()
o7.name = 'DeliveredOrange'  
o7.maxLen = 1000 
o7.queryType = 'measurement_id' 
o7.queryId = meas.id 
o7.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o7.since = None
o7.before = None
o7.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'default':5, 'field': 'string'}
o7.customFilter = {'field': 'string', 'val': 'orange'} 
o7.statsInfo = []
o7.postProc = {'movingCount':'string'}
o7.notNull = 0
o7.save()

c7 = Chart()
c7.name = 'Candies by Color Orange'
c7.olap = o7.name
c7.chartid = c4.id
c7.style = 'area'
c7.minval = 0
c7.maxval = None
c7.xtype = 'datetime'
c7.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c7.color = 'orange'
c7.labelmap = {}
c7.accumulate = False
c7.renderorder = c4.renderorder + 1
c7.halfsize = False
c7.realtime = True
c7.dataMap = ['capturetime','string']
c7.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c7.save()

## Red gumball evaled
o8 = OLAP()
o8.name = 'DeliveredRed'  
o8.maxLen = 1000 
o8.queryType = 'measurement_id' 
o8.queryId = meas.id 
o8.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o8.since = None
o8.before = None
o8.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'default':5, 'field': 'string'}
o8.customFilter = {'field': 'string', 'val': 'red'} 
o8.statsInfo = []
o8.postProc = {'movingCount':'string'}
o8.notNull = 0
o8.save()

c8 = Chart()
c8.name = 'Candies by Color Red'
c8.olap = o8.name
c8.chartid = c4.id
c8.style = 'area'
c8.minval = 0
c8.maxval = None
c8.xtype = 'datetime'
c8.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c8.color = 'red'
c8.labelmap = {}
c8.accumulate = False
c8.renderorder = c4.renderorder + 1
c8.halfsize = False
c8.realtime = True
c8.dataMap = ['capturetime','string']
c8.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c8.save()
"""

## PassFail
o9 = OLAP()
o9.name = 'PassFail'  
o9.maxLen = 1000 
o9.queryType = 'measurement_id' 
o9.queryId = meas.id 
o9.fields = ['capturetime','string', 'measurement_id', 'inspection_id', 'frame_id']
o9.valueMap = {'red': 0, 'green': 1, 'yellow': 2, 'orange': 3, 'purple': 4, 'field': 'string', 'default': 5}
o9.since = None
o9.before = None
o9.customFilter = {} 
o9.statsInfo = []
o9.save()

c9 = Chart()
c9.name = 'Stats'
c9.olap = o9.name
c9.style = 'marbleoverview'
c9.minval = 0
c9.maxval = None
c9.xtype = 'datetime'
c9.colormap = {'0': 'red', '1': 'green', '2': 'yellow','3': u'orange','4': 'purple'}
c9.labelmap = None
#c9.accumulate = True
c9.renderorder = 1
c9.halfsize = False
c9.realtime = True
c9.dataMap = ['capturetime','string']
c9.metaMap = ['measurement_id', 'inspection_id', 'frame_id']
c9.save()
