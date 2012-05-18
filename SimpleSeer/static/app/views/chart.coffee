#SubView = require './subview'
View = require './view'
template = require './templates/chart'
view_helper = require 'lib/view_helper'
application = require 'application'

module.exports = class ChartView extends View
  template: template
  lastupdate: 0
  lastframe: ''
  getRenderData: =>
    retVal = application.charts._byId[@.anchorId]
    if retVal
      return retVal.attributes
    return false
    
  update: =>
    url = "/olap/Motion/limit/500"
    #if @lastupdate
    #  url = url + "/since/" + @lastupdate.toString()
    #else
    #  url = url + "/limit/20"
    $.getJSON(url, (data) =>
      @._drawDataLegacy data
      $('.alert_error').remove();
      return
     ).error =>
       SimpleSeer.alert('Connection lost','error')
  
  catchUp: =>
    url = "/olap/Motion/since/" + parseInt @lastupdate
    obj = @getRenderData()
    $.getJSON(url, (data) =>
      @._drawDataLegacy data
      application.socket.emit 'subscribe', 'OLAP/'+obj.name+'/'
      return
    ).error =>
      SimpleSeer.alert('Connection lost','error')
      
  
  _drawDataLegacy: (data) =>
    if data.data.length == 0
      return
    dd = []
    if !@.chart
      for d in data.data
        x = d[0]*1000
        dd.push {x: d[0]*1000,y:d[1], marker:{enabled:false}, id:d[3], events: {click: application.charts.callFrame}}
        @.lastupdate = d[0]
        application.charts.lastframe = d[3]
      @.drawChart dd
    else
      series = @.chart.series[0]
      for d in data.data
        series.addPoint {x: d[0]*1000,y:d[1], marker:{enabled:false}, id:d[2], events: {click: application.charts.callFrame}} , true , true
        @.lastupdate = d[0]
        application.charts.lastframe = d[3]
  
  _drawData: (data) =>
    dd = []
    if !@.chart
      for d in data
        x = d[0]*1000
        dd.push {x: d.data[0]*1000,y: d.data[1], marker:{enabled:false}, id:d.frame_id, events: {click: application.charts.callFrame}}
        @.lastupdate = d.data[0]
        application.charts.lastframe = d.frame_id
      @.drawChart dd
    else
      series = @.chart.series[0]
      for d in data
        series.addPoint {x: d.data[0]*1000,y: d.data[1], marker:{enabled:false}, id:d.frame_id, events: {click: application.charts.callFrame}} , true , true
        @.lastupdate = d.data[0]
        application.charts.lastframe = d.frame_id

  _update: (data) =>
    @_drawData data.data.m

  drawChart: (data) =>
    renderData = @getRenderData()
    @.chart = new Highcharts.Chart
      #chart: {renderTo: @.anchorId,type: renderData.chartInfo.name.toLowerCase(),className: 'graph'}
      chart: {renderTo: @.anchorId,type: renderData.chartInfo.name.toLowerCase(),animation: false}
      title: {text:null}
      legend: {enabled: false}
      series: [{name: renderData.name,data: data,shadow:false}]
      xAxis: {startOnTick:false}
      yAxis: {title: {text: ''},plotLines: [{value: 0,width: 1,color: '#808080'}],min:0,max:100}
    $('svg>text>tspan').remove()
    application.socket.on "message:OLAP/#{renderData.name}/", @_update
    application.socket.emit 'subscribe', 'OLAP/'+renderData.name+'/'
    return

  render: =>
    super()
    $('#chart-container').append @.$el
    @update()
    #setTimeout @update, 10
    this
