SubView = require './subview'
template = require './templates/frame'
application = require 'application'


module.exports = class FrameView extends SubView
  id: 'frame-view'
  template: template
  
  getRenderData: => application.settings
    
  setVideoFeed: =>
    #TODO this should be refactored when we support multiple cameras
    img = @$el.find('img')
    width = @$el.innerWidth()
    width = 640 if width > 640
    d = new Date()
    img.attr('src', '/videofeed-width'+width+'.mjpeg?' + d.getTime())
    img.attr('width', "100%")
