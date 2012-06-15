Collection = require "./collection"
OLAP = require "../models/OLAP"
ChartView = require '../views/chart'
application = require '../application'


module.exports = class OLAPs extends Collection
  url: "/api/olap"
  model: OLAP
  paused: false
  timeframe:300

  onSuccess: (d1, d2) =>
    d2.sort (a,b) ->
      (a.chartInfo.renderorder || 100) - (b.chartInfo.renderorder || 101)
    for me in d2
      console.log me.name, me.chartInfo.renderorder
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
        #if mod.id == '4fdb762efb920a5ded000007'
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
      _map:['red','green','blue']
      values:{'red':0,'green':0,'blue':0}
      stack:[]
      max: d.chartInfo.max || 100
      min: d.chartInfo.min || 0
      template: _.template '<ul><li style="color:red">{{ values.red }}</li><li style="color:green">{{ values.green }}</li><li style="color:blue">{{ values.blue }}</li></ul>'
      addPoint: (d,shift=true) ->
        #x = Math.floor(((d.x / 1000) % 60) / 20)
        x = d.x
        if shift
          p = @.stack.shift()
          @values[@._map[p.x]] -= p.y
        @.stack.push({x:x,y:d.y})
        @values[@._map[x]] += d.y
      setData: (d) ->
        @stack = []
        for o in d
          @.addPoint o, false
      render: (target) ->
        target.html @.template {values:@.values}
    marbleoverview: (d)->
      name:d.name
      stack:[]
      data:
        served:0
        meantime:0
        failed:0
      max: d.chartInfo.max || 100
      min: d.chartInfo.min || 0
      template: _.template '
        <div id="stats" style="text-align: center; width: 100%; background: #eee; border-radius: 7px; padding: 15px; box-sizing: border-box;">
          <h2>Served: {{data.served}} | Mean Time: {{ data.meantime }} seconds | Fails: {{ data.failed }}</h2>
        </div>'
      addPoint: (d,shift=true) ->
        #x = d.y
        #d.y = d.y
        if shift
          p = @.stack.shift()
          #@values[p.x] -= p.y
        @.stack.push({x:d.x,y:d.y})
        #@values[x] += d.y
      setData: (d) ->
        @stack = []
        for o in d
          @.addPoint o, false
      render: (target) ->
        _counts = [0,0,0]
        _time = 0
        for i in @stack
          _counts[i.y]++
          if !_to
            _to = i.x.unix()
          else
            _time += i.x.unix() - _to
            _to = i.x.unix()
        #console.log _counts
        @data.meantime = _time / @stack.length
        @data.meantime = @data.meantime.toFixed(3)
        @data.served = _counts[1]
        @data.failed = _counts[0]
        target.html @.template {data:@.data,name:@.name}

