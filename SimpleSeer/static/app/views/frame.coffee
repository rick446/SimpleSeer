SubView = require './subview'
template = require './templates/frame'
application = require 'application'


module.exports = class FrameView extends SubView
  id: 'frame-view'
  template: template

  initialize: ()=>
    super()
    application.socket.on "message:capture/", @capturedNewFrame

  getRenderData: => application.settings

  setVideoFeed: =>
    #TODO this should be refactored when we support multiple cameras
    width = @$el.innerWidth()
    width = 640 if width > 640
    d = new Date()
    img = @$el.find('img')
    camera = 0
    for i in img
      $(i).attr('src', '/latestimage-width'+width+'-camera'+camera+'.jpg?' + d.getTime())
      $(i).attr('width', "100%")
      camera = camera + 1

  capturedNewFrame: =>
    if @$el.is ':visible'
      @setVideoFeed()