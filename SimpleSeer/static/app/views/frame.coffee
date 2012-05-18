SubView = require './subview'
template = require './templates/frame'

module.exports = class FrameView extends SubView
  id: 'frame-view'
  template: template

  setVideoFeed: =>
    img = @$el.find('img')
    width = @$el.innerWidth()
    width = 640 if width > 640
    img.attr('src', '/videofeed-width'+width+'.mjpeg?' + Date.UTC())
    img.attr('width', "100%")