View = require './view'
template = require './templates/framelist'
app = require "application"

module.exports = class FramelistView extends View  
  template: template
  
  getRenderData: =>
    @collection = app.lastframes #TODO, want to figure out some way to pass this
    frames: @collection.map (frame) ->
      capturetime: frame.get('capturetime')
      camera: frame.get('camera')
      imgfile: frame.get('imgfile')
      id: frame.get('id')
      
  