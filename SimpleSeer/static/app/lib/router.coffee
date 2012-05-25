require 'lib/slide_replace'
application = require 'application'


module.exports = class Router extends Backbone.Router
  routes:
    '': 'home'
    'frames': 'framelist'

  home: ->
    application.charts.fetch
      success: (d1, d2) ->
        $('#main').slideReplace application.homeView.render().el, 'left'
        application.homeView.subviews.frameview.setVideoFeed()
        application.charts.onSuccess(d1, d2)

  framelist: ->
    application.lastframes.fetch
      success: ->
        $('#main').slideReplace application.framelistView.render().el, 'right'