SubView = require './subview'
template = require './templates/chart'

module.exports = class ChartView extends SubView
  id: 'chart-view'
  template: template
  

  update: =>
    $.getJSON "/olap/Motion", (data) =>
      setTimeout @update, 1000
      d = data.data[data.data.length-1]
      tz = new Date().getTimezoneOffset() * 60 * 1000
      @ts.append d[0] * 1000 + tz, d[1]
      return

  render: =>
    super()
    setTimeout @update, 1000
    smoothie = new SmoothieChart
      grid:
        strokeStyle: 'rgb(0, 144, 214)'
        fillStyle: 'rgb(0, 0, 40)'
        lineWidth: 1
      millisPerPixel: 100
      maxValue: 100
      minValue: 0
        
    @ts = new TimeSeries
    smoothie.streamTo(@$("#motion_canvas")[0])
    smoothie.addTimeSeries @ts,
      strokeStyle: 'rgb(0, 255, 0)'
    
