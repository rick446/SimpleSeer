ChartView = require '../Customcharts'

module.exports = class sumbucket extends ChartView
  
  initialize: (d) =>
    super d
    lib:'custom'
    _map:['red','green','blue']
    values:{'red':0,'green':0,'blue':0}
    stack:[]
    max: d.chartInfo.max || 100
    min: d.chartInfo.min || 0
    template: _.template '<ul><li style="color:red">{{ values.red }}</li><li style="color:green">{{ values.green }}</li><li style="color:blue">{{ values.blue }}</li></ul>'
    this

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
