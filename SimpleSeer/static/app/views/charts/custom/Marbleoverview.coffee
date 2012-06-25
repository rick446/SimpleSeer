ChartView = require '../Customcharts'

module.exports = class marbleoverview extends ChartView
  
  initialize: (d) =>
    super d
    @lib = 'custom'
    @data = {
      served:0
      meantime:0
      failed:0
    }
    @max = @model.chartInfo.max || 100
    @min = @model.chartInfo.min || 0
    @template = _.template '
      <div id="stats" style="text-align: center; width: 100%; background: #eee; border-radius: 7px; padding: 15px; box-sizing: border-box;">
        <h2>Served: {{data.served}} | Mean Time: {{ data.meantime }} seconds | Fails: {{ data.failed }}</h2>
      </div>'
    this

  addPoint: (d) =>
    super d

  setData: (d) =>
    super d

  render: =>
    _counts = [0,0,0]
    _time = 0
    for i in @stack.stack
      _counts[i.y]++
      if !_to
        _to = i.x.unix()
      else
        _time += i.x.unix() - _to
        _to = i.x.unix()
    @data.meantime = _time / @stack.length
    @data.meantime = @data.meantime.toFixed(3)
    @data.served = _counts[1]
    @data.failed = _counts[0]
    super()

  getRenderData: =>
    data:@.data
    name:@.name
