View = require './view'
FrameView = require './frame'
template = require './templates/home'

module.exports = class HomeView extends View
  initialize: =>
    super()
    @addSubview "frame-view", FrameView, '#frame-container'
  id: 'home-view'
  template: template
