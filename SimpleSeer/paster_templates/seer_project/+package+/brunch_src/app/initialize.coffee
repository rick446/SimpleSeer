application = require 'application'

$ ->
  $.getJSON '/settings', (data) ->
    _.templateSettings = {interpolate : /\{\{(.+?)\}\}/g}

    window.SimpleSeer = application
    application.settings = data.settings
    application.initialize()
    Backbone.history.start()
