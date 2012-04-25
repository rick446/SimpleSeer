View = require './view'
template = require './templates/frame'

module.exports = class FrameView extends View
  id: 'frame-view'
  template: template