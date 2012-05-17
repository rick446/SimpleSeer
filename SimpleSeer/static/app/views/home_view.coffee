View = require './view'
FrameView = require './frame'
template = require './templates/home'
application = require 'application'

module.exports = class HomeView extends View
  initialize: =>
    super()
    @addSubview "frame-view", FrameView, '#frame-container'
  id: 'home-view'
  template: template
  getRenderData: =>
    return chartcount : application.charts.length
