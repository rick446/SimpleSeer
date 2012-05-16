SubView = require './subview'
template = require './templates/frame'

module.exports = class FrameView extends SubView
  id: 'frame-view'
  template: template

  initialize: (args...) =>
    super(args...)
    setInterval @rerender, 5000

  rerender: =>
    img = @$('img')
    img.attr('src', '/videofeed.mjpeg?' + Date.UTC()