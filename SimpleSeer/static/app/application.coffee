# The application bootstrapper.
Application =
  initialize: ->
    HomeView = require 'views/home_view'
<<<<<<< HEAD
    FramelistView = require 'views/framelist_view'
=======
    FrameView = require 'views/frame'
>>>>>>> 1f8187ddd285bfbb858e6e36d4c07854f63e29ff
    Router = require 'lib/router'
    Inspections = require 'collections/inspections'
    Measurements = require 'collections/measurements'
    Frames = require 'collections/frames'
    OLAPs = require 'collections/OLAPs'

<<<<<<< HEAD
=======
    # Ideally, initialized classes should be kept in controllers & mediator.
    # If you're making big webapp, here's more sophisticated skeleton
    # https://github.com/paulmillr/brunch-with-chaplin
    @homeView = new HomeView()
>>>>>>> 1f8187ddd285bfbb858e6e36d4c07854f63e29ff
    
    @inspections = new Inspections()
    @inspections.fetch()
    
    @charts = new OLAPs()
    @charts.fetch({success:@charts.onSuccess})
    
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
