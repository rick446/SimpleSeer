Frame = require 'app/models/Frame'
OLAP = require 'app/models/OLAP'
Inspection = require 'app/models/Inspection'
Measurement = require 'app/models/Measurement'

describe 'models/Frame', ->
  o = new Frame()
  describe '#url', ->
    it 'should be /api/frame', ->
      o.url().should.equal '/api/frame'

describe 'models/OLAP', ->
  o = new OLAP()
  describe '#url', ->
    it 'should be /api/olap', ->
      o.url().should.equal '/api/olap'

describe 'models/Inspection', ->
  o = new Inspection()
  describe '#url', ->
    it 'should be /api/inspection', ->
      o.url().should.equal '/api/inspection'

describe 'models/Measurement', ->
  o = new Measurement()
  describe '#url', ->
    it 'should be /api/measurement', ->
      o.url().should.equal '/api/measurement'

