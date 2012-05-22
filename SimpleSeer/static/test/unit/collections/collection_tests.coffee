require.extensions['.hbs'] = (module, filename) ->
  Handlebars = require 'handlebars'
  fs = require 'fs'
  text = fs.readFileSync filename, 'utf8'
  content = Handlebars.compile text,
    filename: filename
  return content

# Units under test
Frames = require 'app/collections/frames'
OLAPs = require 'app/collections/OLAPs'
Inspections = require 'app/collections/Inspections'
Measurements = require 'app/collections/Measurements'

describe 'collections/Frames', ->
  o = new Frames()
  describe '#url', ->
    it 'should be /lastframes', ->
      o.url.should.equal '/lastframes'
  describe '#model', ->
    it 'should be Frame', ->
      o.model.name.should.equal 'Frame'

