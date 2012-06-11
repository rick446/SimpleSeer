Collection = require "./collection"
OLAP = require "../models/OLAP"
ChartView = require '../views/chart'
application = require '../application'


module.exports = class OLAPs extends Collection
  url: "/api/olap"
  model: OLAP
  paused: false
  timeframe:300
  
  customCharts:
    total: (d)->
      color: d.chartInfo.color || 'blue'
      value:0
      values:[]
      max: d.chartInfo.max || 100
      min: d.chartInfo.min || 0
      template: _.template '<h1 style="color:{{ color }}">{{ value }}</h1>'
      addPoint: (d) ->
        @.values.push(d.y)
        if !application.charts.paused && @.values.length > application.charts.timeframe / application.settings.poll_interval
          p = @.values.shift()
        @.value += (d.y - (p || 0))
      setData: (d) ->
        @.values=[]
        @.value=0
        while !application.charts.paused && d.length > application.charts.timeframe / application.settings.poll_interval
          d.shift()
        for o in d
          @.values.push(o.y)
          @.value += o.y
      render: (target) ->
        target.html @.template {value:Math.round(@.value),color:@.color}
    sumbucket: (d)->
      value:0
      values:{'red':0,'green':0,'blue':0}
      stack:[]
      max: d.chartInfo.max || 100
      min: d.chartInfo.min || 0
      template: _.template '<ul><li style="color:red">{{ values.red }}</li><li style="color:green">{{ values.green }}</li><li style="color:blue">{{ values.blue }}</li></ul>'
      addPoint: (d) ->
        if d.y <= 10
          @.values.red++
          val = 'red'
        if d.y > 10 && d.y<= 30
          @.values.green++
          val = 'green'
        if d.y > 30
          @.values.blue++
          val = 'blue'
        @.stack.push(val)
      setData: (d) ->
        for o in d
          @.addPoint o
      render: (target) ->
        target.html @.template {values:@.values}
    

  onSuccess: (d1, d2) =>
    for me in d2
      #d1.buildChart d1.get me.id
      mod = d1.get me.id
      if !mod.view
        cn = ''
        if inHalf
          cn = 'graph-half-size'
          inHalf = false
        else if me.chartInfo.halfsize
          cn = 'graph-half-size'
          inHalf = true
        mod.view = new ChartView({id:me.id,model:me,className:cn})
        #mod.view.anchorId = me.id
        mod.view.render()
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
