View = require './view'
FrameView = require './frame'
application = require 'application'

module.exports = class HomeView extends View
  initialize: =>
    super()
    $.datepicker.setDefaults $.datepicker.regional['']
    @addSubview "frameview", FrameView, '#frame-container'
    $(window).on('scroll', @scrollSearchbar)
    Highcharts.setOptions
      global:
        useUTC: false
      title:
        text:null
      yAxis:
        title:
          text: ''
          style:
            color: '#5B5B5B'
      xAxis:
        title:
          text: ''
          style:
            color: '#5B5B5B'
      tooltip:
        snap:50
        crosshairs:true
        #enabled:false
      plotOptions:
        series:
          #connectNulls: true
          #stickyTracking: false
          lineWidth:1
        area:
          stacking: 'percent'
        pie:
          dataLabels:
            enabled: false
        column:
          dataLabels:
            enabled: true

      credits:
        enabled:
          false
      legend:
        enabled: false
      chart:
        animation: true
  
  events:
    "click #realtimecontrol": "realtimeControl"
    #"click #controlbarchangebtn": "changeTime"
    "click li.timespan_toggle": "toggleTimespanControl"
    "change #chart-interval": "changeInterval"
    
  id: 'home-view'
  template: require application.settings.template_paths['home-view'] || './templates/home'
  getRenderData: =>
    return chartcount : application.charts.length

  postRender: =>
    $('#date-from').datetimepicker {timeFormat: 'hh:mm:ss', onClose: (=> @changeTime())}
    $('#date-to').datetimepicker {timeFormat: 'hh:mm:ss', onClose: (=> @changeTime())}
    $('#chart-interval').selectmenu()
    #$('#chart-interval').attr('value',application.charts.timeframe)
    @_makeNow()
    $('#date-to').attr 'disabled', 'disabled'
    application.framesets.fetch()

  _makeNow: =>
    if !application.charts.paused
      if @_now
        clearInterval @_now
      $('#date-to').datetimepicker('setDate',new Date())
      @_now = setInterval(->
        interval = application.charts.timeframe * 1000
        dt = new Date()
        $('#date-to').datetimepicker('setDate',dt)
        dtt = new Date(dt.getTime() - interval)
        $('#date-from').datetimepicker('setDate',dtt)
      , 1000)
    else
      if @_now
        clearInterval @_now      

  changeInterval: (e)=>
    application.charts.timeframe = e.target.value
    @changeTime()

  realtimeControl: (evt)=>
    if evt
      evt.preventDefault()
    @toggleControlBar()
    if application.charts.paused
      application.charts.unpause()
      $('#date-to').attr 'disabled', 'disabled'
    else
      application.charts.pause()
      $('#date-to').removeAttr "disabled"      
    @_makeNow()
    return
        
  changeTime: =>
    if application.charts.paused
      f = $('#date-from')
      t = $('#date-to')
      dt = new moment()
      if !f.datetimepicker('getDate')
        f.datetimepicker('setDate', dt)
    
      if !t.datetimepicker('getDate')
        t.datetimepicker('setDate', dt.subtract('minutes',1))
    
      _dtf = new moment($('#date-from').datetimepicker('getDate'))
      _dtt = new moment($('#date-to').datetimepicker('getDate'))
      if !_dtf
        _dtf = new moment()
        $('#date-from').datetimepicker('setDate',_dtf)
      if !_dtt
        _dtt = new moment()
        $('#date-to').datetimepicker('setDate',_dtt)
      _dtf = _dtf.utc().valueOf()
      _dtt = _dtt.utc().valueOf()
      for obj in application.charts.models
        obj.view.update _dtf,_dtt
    else
      application.charts.timeframe = $('#chart-interval').attr('value')
      #console.log application.charts.timeframe
      tf = new moment().subtract('seconds',(application.charts.timeframe*1000)).valueOf()
      for obj in application.charts.models
        obj.view.update tf
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

  toggleView: (link, objID) ->
    detector = document.getElementById("frame-container")
    video = document.getElementById("demo_video")
    if link is "detector"
      detector.style.display = "block"
      video.style.display = "none"
    else
      detector.style.display = "none"
      video.style.display = "block"
    linksArray = document.getElementById("toggle").getElementsByTagName("a")
    i = 0
  
    while i < linksArray.length
      linksArray[i].style.color = "#7c7c7c"
      i++
    objID.style.color = "#000000"
