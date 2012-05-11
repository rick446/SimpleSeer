# The application bootstrapper.
Application =
  initialize: ->
    HomeView = require 'views/home_view'
    FrameView = require 'views/frame'
    ChartView = require 'views/chart'
    Router = require 'lib/router'
    Inspections = require 'collections/inspections'
    Measurements = require 'collections/measurements'
    OLAPs = require 'collections/OLAPs'

    # Ideally, initialized classes should be kept in controllers & mediator.
    # If you're making big webapp, here's more sophisticated skeleton
    # https://github.com/paulmillr/brunch-with-chaplin
    @homeView = new HomeView()
    @chartView = new ChartView()
    
    @inspections = new Inspections()
    @inspections.fetch()
    
    @charts = new OLAPs()
    @charts.fetch()
    
    @measurements = new Measurements()
    @measurements.fetch()

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
