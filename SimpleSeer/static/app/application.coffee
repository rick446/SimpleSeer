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

module.exports = Application
