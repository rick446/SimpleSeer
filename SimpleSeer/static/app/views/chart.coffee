View = require './view'

template = require './templates/chart'
view_helper = require '../lib/view_helper'
application = require '../application'

module.exports = class ChartView extends View
  template: template
  lastupdate: 0
  lastframe: ''
  x:0
  getRenderData: =>
    retVal = application.charts._byId[@.anchorId]
    if retVal
      return retVal.attributes
    return false

  update: (frm, to, reset=true )=>
    if frm and to
      url = "/olap/Motion/since/"+frm+"/before/" + to
    else if frm
      url = "/olap/Motion/since/" + frm
    else
      interval = application.settings.poll_interval || 1
      url = "/olap/Motion/limit/"+application.charts.timeframe / interval
    $.getJSON(url, (data) =>
      @._drawDataLegacy data.data,reset
      $('.alert_error').remove()
      return
     ).error =>
       SimpleSeer.alert('Connection lost','error')

  _drawDataLegacy: (data, reset) =>
    if data.length == 0
      return
    dd = []
    for d in data
      dd.push
        data: [d[0], d[1]]
        frame_id: d[3]
    @_drawData dd, reset
  
  _formatChartPoint: (d) =>
    _point =
      x: @x++
      y: d.data[1]
      z:@_formatDate(d.data[0]*1000)
      marker:
        enabled:false
      id:d.frame_id
      events:
        click: application.charts.callFrame

  _drawData: (data,reset) =>
    dd = []
    if !@.chart
      @.drawChart()
      reset = true
    if reset
      for d in data
        dd.push @_formatChartPoint d
      @.lastupdate = d.data[0]
      application.charts.lastframe = d.frame_id
      @.chart.series[0].setData(dd)
    else
      series = @.chart.series[0]
      for d in data
        series.addPoint(@_formatChartPoint(d),true,true)
        @.lastupdate = d.data[0]
        application.charts.lastframe = d.frame_id

  _update: (data) =>
    @_drawData data.data.m

  _formatDate: (dt) =>
    dt = new Date(dt)
    s = dt.getSeconds()
    m = dt.getMinutes()
    h = dt.getHours()
    if s < 10
      s = '0' + String(s)
    if m < 10
      m = '0' + String(m)
    if h < 10
      h = '0' + String(h)
    return  h + ':' + m + ':' + s

  drawChart: (data) =>
    renderData = @getRenderData()
    @.chart = new Highcharts.Chart
      chart:
        renderTo: @.anchorId
        type: renderData.chartInfo.name.toLowerCase()
        animation: false
      title:
        text:null
      credits:
        enabled:
          false
      legend:
        enabled: false
      plotOptions:
        series:
          stickyTracking: false
          lineWidth:2
      series: [{name: renderData.name,data: [],shadow:false, color: renderData.chartInfo.color}]
      tooltip:
        headerFormat:
          ''
        pointFormat:
          '<small>{point.z}</small><br><b>{point.y}% movement</b>'
      animation:
        duration:
          10
      xAxis:
        labels:
          enabled:false
      yAxis:
        title:
          text: ''
        min:0
        max:100

    application.socket.on "message:OLAP/#{renderData.name}/", @_update
    application.socket.emit 'subscribe', 'OLAP/'+renderData.name+'/'
    return

  render: =>
    super()
    $('#chart-container').append @.$el
    @update null,null,true
    this
