View = require './view'
FrameView = require './frame'
ChartView = require './chart'
template = require './templates/home'

module.exports = class HomeView extends View
  initialize: =>
    super()
    @addSubview "frame-view", FrameView, '#frame-container'
    @addSubview "chart-view", ChartView, '#chart-container'
  id: 'home-view'
  template: template
