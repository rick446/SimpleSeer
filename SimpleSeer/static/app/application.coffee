# The application bootstrapper.
Application =
  initialize: ->
    if @settings.mongo.is_slave
      $(".notebook").hide()
      
    ViewHelper = require 'lib/view_helper'
    HomeView = require 'views/home_view'
    FramelistView = require 'views/framelist_view'
    FrameDetailView = require 'views/framedetail_view'
    #FrameSetView = require 'views/frameset_view'
    Router = require 'lib/router'
    Inspections = require 'collections/inspections'
    Measurements = require 'collections/measurements'
    Frames = require 'collections/frames'
    OLAPs = require 'collections/OLAPs'
    FrameSets = require 'collections/framesets'

    @.socket = io.connect '/rt'
    @.socket.on 'connect', ->
      #alert 'connect'
    @.socket.on 'error', ->
      #alert 'error'
    @.socket.on 'disconnect', ->
      #alert 'disconnect'
    #@.socket.on 'message', (msg) ->
    #  console.log 'Got message', msg
    @.socket.on "message:alert/", @_serveralert
    @.socket.emit 'subscribe', 'alert/'

    @inspections = new Inspections()
    @inspections.fetch()
    @charts = new OLAPs()
    @measurements = new Measurements()
    @measurements.fetch()
    @frames = new Frames()
    @framesets = new FrameSets()

    @lastframes = new Frames()

    @homeView = new HomeView()
    @framelistView = new FramelistView(@lastframes)

    # set up the timeout message dialog
    $('#lost_connection').dialog
      autoOpen: false
      modal: true
      buttons:
        Ok: ->
          $( this ).dialog( "close" )

    # Instantiate the router
    @router = new Router()
    # Freeze the object
    Object.freeze? this

  _serveralert: (msg) ->
    Application.alert(msg['data']['message'], msg['data']['severity'])

  alert: (message, alert_type) ->
	
    _set = true
    if alert_type == 'clear'
      $("#messages > .alert").hide 'slow', -> $("#messages").html('')
    else if alert_type == "redirect"
      Application.router.navigate(message, true)
    else
      $(".alert_"+alert_type).each (e,v)->
        if v.innerHTML == message
          _set = false
      if _set
        div = $("<div>",
          style: "display: none",
          class: "alert alert"+alert_type
        ).html message
        $("#messages").append div
        div.show('normal')
        

module.exports = Application
