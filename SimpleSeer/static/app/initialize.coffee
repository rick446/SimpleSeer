application = require 'application'

$ ->
  application.initialize()
  window.SimpleSeer = application
  Backbone.history.start()
  window.SimpleSeer = application
