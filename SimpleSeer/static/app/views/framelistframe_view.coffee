View = require './view'
template = require './templates/framelistframe'

module.exports = class FramelistFrameView extends View
  template: template

  initialize: (frame)=>
    super()
    @frame = frame

  getRenderData: =>
    capturetime: new Date parseInt @frame.get('capturetime')+'000'
    camera: @frame.get('camera')
    imgfile: @frame.get('imgfile')
    id: @frame.get('id')