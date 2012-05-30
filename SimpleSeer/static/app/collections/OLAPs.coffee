Collection = require "./collection"
OLAP = require "../models/OLAP"
ChartView = require '../views/chart'
application = require '../application'


module.exports = class OLAPs extends Collection
  url: "/api/olap"
  model: OLAP
  paused: false
  timeframe:60

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
    control.html "Realtime"
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
    control.html "Pause"
    for obj in @.models
      interval = application.settings.poll_interval || 1
      tf = Math.round((new Date()).getTime() / 1000) - Math.ceil(application.charts.timeframe / interval)
      obj.view.update parseInt(tf)
      application.socket.emit 'subscribe', 'OLAP/'+obj.attributes.name+'/'
    $('.alert_error').remove()
    fDom = $('#frame img')
    fDom.attr('src',fDom.attr('live'))

  callFrame: (e) =>
    if e.point.config.id
      @.pause(e.point.config.id)

  overPoint: (e) =>
    for m in application.charts.models
      m.view.chart.tooltip.refresh m.view.chart.get e.target.id
