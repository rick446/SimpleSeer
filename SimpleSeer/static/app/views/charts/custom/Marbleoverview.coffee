ChartView = require '../Customcharts'

module.exports = class marbleoverview extends ChartView
  
  initialize: (d) =>
    @data = {
      total:0
      meantime:0
      colors:{}
      shortest:0
      longest:0
    }
    @resetColors()
    @max = @model.max || 100
    @min = @model.min || 0
    @template = _.template '
      <div id="stats" class="stats">
        <h2>{{name}}</h2>
        <p><label>Number Served:</label> {{data.total}}</p>
        <p><label>Average Time:</label> {{ data.meantime }} seconds</p>
        <p><label>Fastest Time:</label> {{data.shortest}} seconds</p>
        <p><label>Colors Analyzed:</label>
        <div style="float:left;margin-top:-3px;">
          <div class="swatch" style="border: 2px solid {{ colormap[0]}}">{{ data.colors[0] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[1]}}">{{ data.colors[1] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[2]}}">{{ data.colors[2] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[3]}}">{{ data.colors[3] }}</div>
          <div class="swatch" style="border: 2px solid {{ colormap[4]}}">{{ data.colors[4] }}</div>
        </div>

        </p>
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
        _to = i.x.valueOf() / 1000
      else
        _diff = i.x.valueOf() / 1000 - _to
        _time += _diff
        _to = i.x.valueOf() / 1000
        if _diff and (_diff < @data.shortest or @data.shortest == 0) 
          @data.shortest = _diff.toFixed(3)
        if _diff and (_diff > @data.longest or @data.shortest == 0)
          @data.longest = _diff.toFixed(3)
        
    #console.log _time, @stack.stack.length
    @data.meantime = _time / @stack.stack.length
    @data.meantime = @data.meantime.toFixed(3)
    if isNaN @data.meantime
      @data.meantime = 0
    @data.total = _total
    @$el.html @template @getRenderData()

  #getRender: =>
  #  _.template @template, @data

  getRenderData: =>
    data:@data
    name:@name
    colormap:@model.colormap
