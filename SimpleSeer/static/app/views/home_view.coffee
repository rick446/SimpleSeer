View = require './view'
FrameView = require './frame'
template = require './templates/home'
application = require 'application'

module.exports = class HomeView extends View
  initialize: =>
    super()
    @addSubview "frameview", FrameView, '#frame-container'
    
  
  events:
    "click #realtimecontrol": "realtimeControl"
    
  id: 'home-view'
  template: template
  getRenderData: =>
    return chartcount : application.charts.length


  realtimeControl: =>
    
    if !application.charts.paused
      application.charts.pause()
    else
      application.charts.unpause()
    #control.toggleClass "active"
    return
