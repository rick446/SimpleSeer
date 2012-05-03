# The application bootstrapper.
Application =
  initialize: ->
    HomeView = require 'views/home_view'
    FrameView = require 'views/frame'
    ChartView = require 'views/chart'
    Router = require 'lib/router'
    OLAP = require 'models/olap'

    # Ideally, initialized classes should be kept in controllers & mediator.
    # If you're making big webapp, here's more sophisticated skeleton
    # https://github.com/paulmillr/brunch-with-chaplin
    @homeView = new HomeView()
    @chartView = new ChartView()
    @charts = new Backbone.Collection

    @charts.url = OLAP.url
    @charts.fetch()

    # Instantiate the router
    @router = new Router()
    # Freeze the object
    Object.freeze? this

module.exports = Application
