View = require './view'
FrameView = require './frame'
template = require './templates/home'
application = require 'application'

module.exports = class HomeView extends View
  initialize: =>
    super()
    @addSubview "frameview", FrameView, '#frame-container'
  
  events:
    "click #realtimecontrol": "realtimeControl"
    "click #controlbarchangebtn": "changeTime"
    
  id: 'home-view'
  template: template
  getRenderData: =>
    return chartcount : application.charts.length

  postRender: =>
    $('#date-from').datetimepicker $.datepicker.regional[""]
    $('#date-to').datetimepicker $.datepicker.regional[""]
    $('#chart-interval').attr('value',application.charts.timeframe)

  realtimeControl: =>
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
        obj.view.update(_dtf,_dtt,true)
    else
      application.charts.timeframe = $('#chart-interval').attr('value')
      for obj in application.charts.models
        obj.view.update(null,null,application.charts.timeframe)
      
  
  toggleControlBar: =>
    $('#control-bar-realtime').toggleClass 'hidden'
    $('#control-bar-paused').toggleClass 'hidden'
    return
