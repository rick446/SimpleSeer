View = require './view'
FrameView = require './frame'
template = require './templates/home'
application = require 'application'

module.exports = class HomeView extends View
  initialize: =>
    super()
    @addSubview "frameview", FrameView, '#frame-container'
    $(window).on('scroll', @scrollSearchbar)
  
  events:
    "click #realtimecontrol": "realtimeControl"
    "click #controlbarchangebtn": "changeTime"
    "click li.timespan_toggle": "toggleTimespanControl"
    
  id: 'home-view'
  template: template
  getRenderData: =>
    return chartcount : application.charts.length

  postRender: =>
    $('#date-from').datetimepicker $.datepicker.regional[""]
    $('#date-to').datetimepicker $.datepicker.regional[""]
    $('#chart-interval').attr('value',application.charts.timeframe)

  realtimeControl: (evt)=>
    evt.preventDefault()
    @toggleControlBar()
    if application.charts.paused
      application.charts.unpause()
    else
      application.charts.pause()
    return
  
  changeTime: =>
    if application.charts.paused
      _dtf = $('#date-from').datetimepicker('getDate')
      _dtt = $('#date-to').datetimepicker('getDate')
      if !_dtf
        _dtf = new Date()
        $('#date-from').datetimepicker('setDate',_dtf)
      if !_dtt
        _dtt = new Date()
        $('#date-to').datetimepicker('setDate',_dtt)
      _dtf = _dtf.getTime() / 1000
      _dtt = _dtt.getTime() / 1000
      for obj in application.charts.models
        obj.view.update _dtf,_dtt
    else
      application.charts.timeframe = $('#chart-interval').attr('value')
      for obj in application.charts.models
        obj.view.update()
      
  toggleControlBar: =>
    $('#control-bar-realtime').toggleClass 'hide'
    $('#control-bar-paused').toggleClass 'hide'
    return

  toggleTimespanControl: (evt)->
    evt.preventDefault()
    time_controls = $('#search_bar li.time_controls')
    search_box = $('#search_bar input.search')
    initial_time_width = time_controls.width()
    initial_search_width = search_box.width()
    direction = 1
    if time_controls.is ":hidden"
      direction = -1
    time_controls.animate({width:'toggle'},{
      step: (now, fx) ->
        if direction == 1
          width = initial_search_width+initial_time_width-now
        else
          width = initial_search_width-now
        search_box.width(width)
    })

  # only needed until subnav is supported in bootstrap https://github.com/twitter/bootstrap/issues/1189
  scrollSearchbar: =>
    search_bar = $('#search_bar')
    if $(window).scrollTop() >= 17
      search_bar.addClass 'subnav-fixed'
    else
      search_bar.removeClass 'subnav-fixed'
