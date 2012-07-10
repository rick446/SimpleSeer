ChartView = require '../Customcharts'

module.exports = class marbleoverview extends ChartView
  
  initialize: (d) =>
    @data = {
      total:0
      meantime:0
      colors:{}
      shortest:999999999999
      longest:0
    }
    @resetColors()
    @max = @model.max || 100
    @min = @model.min || 0
    @template = _.template '
      <div id="stats" style="">
        <h2>{{name}}</h2>
        <div style="float:left; margin:0 10px;">
          <div class="swatch" style="border: 2px solid {{ colormap[0]}}">{{ data.colors[0] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[1]}}">{{ data.colors[1] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[2]}}">{{ data.colors[2] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[3]}}">{{ data.colors[3] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[4]}}">{{ data.colors[4] }}</div>
        </div>
        <h3>Number Served: {{data.total}}</h3>
        <h3>Average Time: {{ data.meantime }} seconds</h3>
        <h3>Fastest Time: {{data.shortest}}</h3>
        <h3>Slowest Time: {{data.longest}}</h3>
        <div style="clear:both;"></div>
      </div>'
    super d
    #@.render($('#'+@id))
    this

  addPoint: (d) =>
    super d
    @setData()

  resetColors: =>
    for i,cm of @model.colormap
      @data.colors[i] = 0

  setData: (d, reset) =>
    if d
      super d, reset
    _counts = [0,0,0]
    _time = 0
    _total = 0
    @resetColors()
    for i in @stack.stack
      @data.colors[i.y]++
      _total++
      if !_to
        _to = i.x.unix()
      else
        _diff = i.x.unix() - _to
        _time += _diff
        _to = i.x.unix()
        if _diff and _diff < @data.shortest
          @data.shortest = _diff
        if _diff and _diff > @data.longest
          @data.longest = _diff
        
    #console.log _time, @stack.stack.length
    @data.meantime = _time / @stack.stack.length
    @data.meantime = @data.meantime.toFixed(3)
    @data.total = _total
    @$el.html @template @getRenderData()

  #getRender: =>
  #  _.template @template, @data

  getRenderData: =>
    data:@data
    name:@name
    colormap:@model.colormap
