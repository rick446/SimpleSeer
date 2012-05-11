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
      if data.data.length == 0
        setTimeout @update, 1000
        return
      @lastupdate = data.data[data.data.length-1][0]

      if not @smoothie.seriesSet.length
        @ts = new TimeSeries

        delay = new Date().getTime() - @lastupdate * 1000
        delay = delay * 1.1 #a little extra padding
        @smoothie.streamTo(@$("#motion_canvas")[0], delay)
        @smoothie.addTimeSeries @ts,
          strokeStyle: 'rgb(0, 255, 0)'

      setTimeout @update, 1000
      @lastupdate = data.data[data.data.length-1][0]
      tz = new Date().getTimezoneOffset() * 60 * 1000
      for d in data.data
        @ts.append d[0] * 1000, d[1]
      return

  render: =>
    super()
    setTimeout @update, 10
    @$("#motion_canvas")[0].width = 630 #TODO, fix this by checking it post-render
    @smoothie = new SmoothieChart
      grid:
        strokeStyle: 'rgb(0, 144, 214)'
        fillStyle: 'rgb(0, 0, 40)'
        lineWidth: 1
        millisPerLine: 10000
      millisPerPixel: 200
      maxValue: 100
      minValue: 0




