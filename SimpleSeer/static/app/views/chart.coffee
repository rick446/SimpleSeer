SubView = require './subview'
template = require './templates/chart'
view_helper = require 'lib/view_helper'

module.exports = class ChartView extends SubView
  id: 'chart-view'
  template: template
  lastupdate: 0

  update: =>
  
    url = "/olap/Motion"
    
    if @lastupdate
      url = url + "/since/" + @lastupdate.toString()
      
    
    $.getJSON url, (data) =>
      setTimeout @update, 1000
      @lastupdate = data.data[data.data.length-1][0]
      
      for d in data
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
    
