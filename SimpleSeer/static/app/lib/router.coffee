application = require 'application'


module.exports = class Router extends Backbone.Router
  routes:
    '': 'home'
    'frames': 'framelist'

  home: ->
    application.charts.fetch
      success: (d1, d2) ->
        $('#main').html application.homeView.render().el
        application.homeView.subviews.frameview.setVideoFeed()
        application.charts.onSuccess(d1, d2)

  framelist: ->
    application.lastframes.fetch
      success: ->
        $('#main').html application.framelistView.render().el