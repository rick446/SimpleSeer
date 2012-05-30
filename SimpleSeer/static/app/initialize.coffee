application = require 'application'

$ ->
  $.getJSON '/settings', (data) ->
    application.settings = data.settings
    application.initialize()
    Backbone.history.start()
    window.SimpleSeer = application
