#SubView = require './subview'
View = require './view'
template = require './templates/chart'
view_helper = require 'lib/view_helper'
application = require 'application'

module.exports = class ChartView extends View
  template: template
  lastupdate: 0
  getRenderData: =>
    retVal = application.charts._byId[@.anchorId]
    if retVal
      return retVal.attributes
    return false
    
  update: =>

    url = "/olap/Motion"
    if @lastupdate
      url = url + "/since/" + @lastupdate.toString()
    else
      #todo: set limit
      url = url + "/limit/500"
    $.getJSON(url, (data) =>
      if data.data.length == 0
        setTimeout @update, 1000
        return
   
      @lastupdate = data.data[data.data.length-1][0]
      dd = []
      if !@.chart
        for d in data.data
          x = new Date(d[0])
          dd.push {x:x,y:d[1],marker:{enabled:false}}
        @.drawChart dd
      else
        series = @.chart.series[0]
        for d in data.data
          series.addPoint {x: new Date(d[0]),y: d[1], marker:{enabled:false}} , true , true

      setTimeout @update, 1000
      @lastupdate++
      tz = new Date().getTimezoneOffset() * 60 * 1000
      $('.alert_error').remove();
      return
     ).error =>
       SimpleSeer.alert('Connection lost','error')
       setTimeout @update, 1000

  drawChart: (data) =>
    renderData = @getRenderData()
    @.chart = new Highcharts.Chart
      chart: {renderTo: @.anchorId,type: renderData.chartInfo.name.toLowerCase(),marginRight: 10}
      series: [{name: renderData.name,data: data}]
      xAxis: {type: 'datetime',tickPixelInterval: 150}
      yAxis: {title: {text: 'Value'},plotLines: [{value: 0,width: 1,color: '#808080'}],min:0}

  render: =>
    super()
    $('#chart-container').append @.$el
    setTimeout @update, 10
    this
