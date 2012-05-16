application = require 'application'


module.exports = class Router extends Backbone.Router
  routes:
    '': 'home'
    'frames': 'framelist'

  home: ->
    application.charts.fetch
      success: ->
        $('#main').html application.homeView.render().el    
        application.charts.onSuccess()

  framelist: ->
    application.lastframes.fetch
      success: ->
        $('#main').html application.framelistView.render().el