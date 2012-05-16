application = require 'application'


module.exports = class Router extends Backbone.Router
  routes:
    '': 'home'
    'frames': 'framelist'

  home: ->
    $('#main').html application.homeView.render().el
    
  framelist: ->
    application.lastframes.fetch
      success: ->
        $('#main').html application.framelistView.render().el