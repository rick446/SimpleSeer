application = require 'application'

$ ->
  application.initialize()
  Backbone.history.start()
  window.SimpleSeer = application