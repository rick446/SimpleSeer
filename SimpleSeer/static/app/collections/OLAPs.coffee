Collection = require "./collection"
OLAP = require "../models/OLAP"
ChartView = require '../views/chart'
application = require '../application'
charts = require '../views/charts/init'


module.exports = class OLAPs extends Collection
  url: "/api/chart"
  model: OLAP
  paused: false
  timeframe:300

  onSuccess: (d1, d2) =>
    d2.sort (a,b) ->
      (a.renderorder || 100) - (b.renderorder || 101)
    for me in d2
      #console.log me.name, me.renderorder
      #d1.buildChart d1.get me.id

      mod = d1.get me.id
      if !mod.view
        cn = ''
        if inHalf
          cn = 'graph-half-size'
          inHalf = false
        else if me.halfsize
          cn = 'graph-half-size'
          inHalf = true
        #mod.view = new ChartView({id:me.id,model:me,className:cn})
        if charts[me.style]
          mod.view = new charts[me.style]({id:me.id,model:me,className:cn})
          mod.view.render()
        else
          console.error me.style + ' is not a valid chart type'
    return

  previewImage: (fId) =>
    if application.charts.paused
      @.changeFrameImage fId

  unclickPoint: (fId) =>
    for m in @.models
      if m.view.chart._c.get
        p = m.view.chart._c.get fId
        if p && p.marker && p.marker.radius > 2
          p.update({ marker: {}},true)
    return false

  changeFrameImage: (fId) =>
    fDom = $('#frame img')
    if !fDom.attr('live')
      fDom.attr('live',fDom.attr('src'))
    fDom.attr('src','/grid/imgfile/'+fId)

  pause: (fId) =>
    @.paused = true
    control = $ "#realtimecontrol"
    control.html "History"
    control.attr "title", "Click to enter live mode"
    if !fId
      fId = @lastframe
    @.changeFrameImage fId
    if application.socket
      for obj in @.models
        application.socket.emit 'unsubscribe', 'OLAP/'+obj.attributes.name+'/'
    #application.alert('<a href="#">Pause</a>','error')

  unpause: =>
    @.paused = false
    control = $ "#realtimecontrol"
    control.html "Live"
    control.attr "title", "Click to pause"
    for obj in @.models
      tf = Math.round((new Date()).getTime() / 1000) - application.charts.timeframe
      obj.view.update parseInt(tf)
      if application.socket
        application.socket.emit 'subscribe', 'OLAP/'+obj.attributes.name+'/'
    $('.alert_error').remove()
    fDom = $('#frame img')
    fDom.attr('src',fDom.attr('live'))
    $('#preview').html ''

  callFrame: (e) =>
    if !@.paused
      application.homeView.realtimeControl()
      #@.pause(e.point.config.id)
      
  addFrame: (id) =>
    if !@.paused
      application.homeView.realtimeControl()
    @.pause id
    if application.framesets.models[0]
      application.framesets.models[0].addFrame(id)
    #$('#preview').append '<img style="width:100px" id="image_'+e.target.id+'" src="/grid/imgfile/'+e.target.id+'">'
  
  removeFrame: (id) =>
    $('#image_'+id).remove()
