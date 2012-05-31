application = require 'application'

$ ->
  $.getJSON '/settings', (data) ->
    _.templateSettings = {interpolate : /\{\{(.+?)\}\}/g}

    application.settings = data.settings
    application.initialize()
    Backbone.history.start()
    window.SimpleSeer = application
