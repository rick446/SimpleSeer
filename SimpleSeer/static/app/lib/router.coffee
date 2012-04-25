application = require 'application'


module.exports = class Router extends Backbone.Router
  routes:
    '': 'home'

  home: ->
    $('#main').html application.homeView.render().el
    $('#frame-container').html application.frameView.render().el

    $('#chart-container').append application.chartView.render().el
    $('#chart-container').append application.chartView.render().el