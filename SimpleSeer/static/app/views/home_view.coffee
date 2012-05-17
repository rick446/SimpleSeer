View = require './view'
FrameView = require './frame'
template = require './templates/home'
application = require 'application'

module.exports = class HomeView extends View
  initialize: =>
    super()
    @addSubview "frame-view", FrameView, '#frame-container'
    
  
  events:
    "click #realtimecontrol": "realtimeControl"
    
  id: 'home-view'
  template: template
  getRenderData: =>
    return chartcount : application.charts.length

  realtimeControl: =>
    control = $ "#realtimecontrol"
    
    if control.hasClass "active"
      application.charts.pause()
      control.html "Paused"
    else
      application.charts.unpause()
      control.html "Realtime"

    control.toggleClass "active"
    