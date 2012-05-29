SubView = require './subview'
template = require './templates/frame'

module.exports = class FrameView extends SubView
  id: 'frame-view'
  template: template

  setVideoFeed: =>
    img = @$el.find('img')
    width = @$el.innerWidth()
    width = 640 if width > 640
    d = new Date()
    img.attr('src', '/videofeed-width'+width+'.mjpeg?' + d.getTime())
    img.attr('width', "100%")
