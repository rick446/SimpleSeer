# Units under test
Frames = require 'app/collections/frames'
OLAPs = require 'app/collections/OLAPs'
Inspections = require 'app/collections/Inspections'
Measurements = require 'app/collections/Measurements'

# Require the models for some assertions
Frame = require 'app/models/Frame'
OLAP = require 'app/models/OLAP'
Inspection = require 'app/models/Inspection'
Measurement = require 'app/models/Measurement'

describe 'collections/Frames', ->
  o = new Frames()
  describe '#url', ->
    it 'should be /lastframes', ->
      o.url().should.equal '/lastframes'
  describe '#model', ->
    it 'should be Frame', ->
      o.model.should.equal Frame

