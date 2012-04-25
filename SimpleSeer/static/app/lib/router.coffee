application = require 'application'


module.exports = class Router extends Backbone.Router
  routes:
    '': 'home'

  home: ->
    $('#main').html application.homeView.render().el
