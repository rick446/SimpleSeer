# The application bootstrapper.
Application =
  initialize: ->
    HomeView = require 'views/home_view'
    FramelistView = require 'views/framelist_view'
    FrameView = require 'views/frame'
    Router = require 'lib/router'
    Inspections = require 'collections/inspections'
    Measurements = require 'collections/measurements'
    Frames = require 'collections/frames'
    OLAPs = require 'collections/OLAPs'

    @homeView = new HomeView()

    @.socket = io.connect '/rt'
    @.socket.on 'connect', ->
      alert 'connect'
    @.socket.on 'error', ->
      alert 'error'
    @.socket.on 'disconnect', ->
      alert 'disconnect'
    #@.socket.on 'message', (msg) ->
    #  console.log 'Got message', msg
    
    @inspections = new Inspections()
    @inspections.fetch()
    @charts = new OLAPs()    
    @measurements = new Measurements()
    @measurements.fetch()
    
    @lastframes = new Frames()


    @homeView = new HomeView()
    @framelistView = new FramelistView()


    # Instantiate the router
    @router = new Router()
    # Freeze the object
    Object.freeze? this

  alert: (message, alert_type) ->
    _set = true
    $(".alert_"+alert_type).each (e,v)->
      if v.innerHTML == message
        _set = false
    if _set
      $("#messages").append('<div class="alert alert_'+alert_type+'">'+message+'</div>')

module.exports = Application
