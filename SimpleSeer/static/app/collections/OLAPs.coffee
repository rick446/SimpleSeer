Collection = require "./collection"
OLAP = require "../models/OLAP"
ChartView = require '../views/chart'
application = require '../application'


module.exports = class OLAPs extends Collection
  url: "/api/olap"
  model: OLAP
  paused: false
  timeframe:60
  
  customCharts:
    text: (d)->
      color: d.chartInfo.color || 'blue'
      value:0
      template: _.template '<h1 style="color:{{ color }}">{{ value }}</h1>'
      addPoint: (d) ->
        @.value += d.y
      setData: (d) ->
        for o in d
          @.value += o.y
      render: (target) ->
        target.html @.template {value:Math.round(@.value),color:@.color}

  onSuccess: (d1, d2) =>
    for me in d2
      #d1.buildChart d1.get me.id
      mod = d1.get me.id
      if !mod.view
        mod.view = new ChartView()
        mod.view.anchorId = me.id
        mod.view.render()
    return

  pause: (fId) =>
    @.paused = true
    control = $ "#realtimecontrol"
    control.html "History"
    control.attr "title", "Click to enter live mode"
    if !fId
      fId = @lastframe
    fDom = $('#frame img')
    if !fDom.attr('live')
      fDom.attr('live',fDom.attr('src'))
    fDom.attr('src','/grid/imgfile/'+fId)
    for obj in @.models
      application.socket.emit 'unsubscribe', 'OLAP/'+obj.attributes.name+'/'
    #application.alert('<a href="#">Pause</a>','error')

  unpause: =>
    @.paused = false
    control = $ "#realtimecontrol"
    control.html "Live"
    control.attr "title", "Click to pause"
    for obj in @.models
      interval = application.settings.poll_interval || 1
      tf = Math.round((new Date()).getTime() / 1000) - Math.ceil(application.charts.timeframe / interval)
      obj.view.update parseInt(tf)
      application.socket.emit 'subscribe', 'OLAP/'+obj.attributes.name+'/'
    $('.alert_error').remove()
    fDom = $('#frame img')
    fDom.attr('src',fDom.attr('live'))
    $('#preview').html ''

  callFrame: (e) =>
    if e.point.config.id
      @.pause(e.point.config.id)
      
  addFrame: (e) =>
    $('#preview').append '<img style="width:100px" id="image_'+e.target.id+'" src="/grid/imgfile/'+e.target.id+'">'
  
  removeFrame: (e) =>
    $('#image_'+e.target.id).remove()
