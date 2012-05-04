SubView = require './subview'
template = require './templates/frame'

module.exports = class FrameView extends SubView
  id: 'frame-view'
  template: template

  update: =>
    time = new Date().getTime().toString()
    setTimeout @update, 1000
    @$el.find("img").attr("src", "/frame?" + time)

  render: =>
    setTimeout @update, 1000
    super()