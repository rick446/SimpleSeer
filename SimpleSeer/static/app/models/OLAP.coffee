Model = require "./model"

module.exports = class OLAP extends Model
  urlRoot: -> "/api/olap"


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
      stack:[]
      data:
        served:0
        meantime:0
        failed:0
      max: d.chartInfo.max || 100
      min: d.chartInfo.min || 0
      template: _.template '
      <div id="stats-container" class="span2">
        <div id="stats" style="text-align: center; width: 100%; margin-top: 35px; background: #eee; border-radius: 7px; padding: 15px; box-sizing: border-box;">
          <h1>Gumballs</h1><hr>
          <h2>Served:</h2>
          <h3>{{data.served}}%</h3><hr>
          <h2>Mean Time:</h2>
          <h3>{{ data.meantime }}</h3><hr>
          <h2>Fails:</h2>
          <h3>{{ data.failed }}</h3><hr>
        </div>
      </div>'
      addPoint: (d,shift=true) ->
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
        _counts = [0,0,0]
        for i in @stack
          _counts[i.x]++
          _time += i.y
        @data.meantime = _time / @stack.length
        @data.served = _counts[1]
        @data.failed = _counts[0]
        target.html @.template {data:@.data}

  pointStack: () ->
    stack : []
    add: (d,shift=true) ->
      @.stack.push {x:d.x.toString(),y:d.y,id:d.id.toString()}
      if shift
        p = @.stack.shift()
      return p
    set: (d) ->
      @stack = []
      for o in d
        @.add o, false
    buildData: (data) =>
      if !data
        data = @.view.chart.stack.stack
      dd = []
      if @.attributes.chartInfo.map
        for i of @.attributes.chartInfo.map
          dd[i] = {x:i,id:i,y:0}
          if @.attributes.chartInfo.colormap && @.attributes.chartInfo.colormap[i]
            dd[i].color = @.attributes.chartInfo.colormap[i]
      _stk = []
      for d in data
        if !d.x
          p = @.view._formatChartPoint d
        else p = d
        if dd[p.id]
          p = dd[p.id]
          p.y++
        else
          p.y = 1
        dd[p.id] = p
        _stk.push p
      _dd = []
      for i in dd
        if i
          _dd.push i
      @.view.chart.stack.set _stk
      return _dd
  


