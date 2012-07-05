ChartView = require '../Customcharts'

module.exports = class marbleoverview extends ChartView
  
  initialize: (d) =>
    @data = {
      served:0
      meantime:0
      failed:0
    }
    @max = @model.max || 100
    @min = @model.min || 0
    @template = _.template '
      <div id="stats" style="text-align: center; width: 100%; background: #eee; border-radius: 7px; padding: 15px; box-sizing: border-box;">
        <h2>Served: {{data.served}} | Mean Time: {{ data.meantime }} seconds | Fails: {{ data.failed }}</h2>
      </div>'
    super d
    #@.render($('#'+@id))
    this

  addPoint: (d) =>
    super d
    #console.log d
    @setData()


  setData: (d) =>
    if d
      super d
    _counts = [0,0,0]
    _time = 0
    for i in @stack.stack
      _counts[i.y]++
      if !_to
        _to = i.x.unix()
      else
        _time += i.x.unix() - _to
        _to = i.x.unix()
    #console.log _time, @stack.stack.length
    @data.meantime = _time / @stack.stack.length
    @data.meantime = @data.meantime.toFixed(3)
    @data.served = _counts[1]
    @data.failed = _counts[0]
    @$el.html @template @getRenderData()

  #getRender: =>
  #  _.template @template, @data

  getRenderData: =>
    data:@.data
    name:@.name
