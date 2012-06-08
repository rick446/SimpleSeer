View = require './view'

template = require './templates/chart'
view_helper = require '../lib/view_helper'
application = require '../application'

module.exports = class ChartView extends View
  template: template
  lastupdate: 0
  lastframe: ''
  getRenderData: =>
    retVal = application.charts._byId[@.anchorId]
    if retVal
      return retVal.attributes
    return false

  update: (frm, to, reset=true )=>
    name = application.charts._byId[@.anchorId].attributes.name
    if frm and to
      url = "/olap/"+name+"/since/"+frm+"/before/" + to
    else if frm
      url = "/olap/"+name+"/since/" + frm
    else
      interval = application.settings.poll_interval || 1
      url = "/olap/"+name+"/limit/"+Math.ceil(application.charts.timeframe / interval)
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
      y:Math.round(d.data[1])
      x:moment(d.data[0]*1000)
      id:d.frame_id
      events:
        #click: application.charts.callFrame
        mouseOver: @.overPoint
        click: @.clickPoint #application.charts.addFrame
        #unselect: @.unselectPoint #application.charts.removeFrame

  overPoint: (e) =>
    if application.charts._imageLoader
      clearInterval application.charts._imageLoader
    application.charts._imageLoader = setTimeout (->
      application.charts.previewImage e.target.id
    ), 500
    for m in application.charts.models
      m.view.chart.showTooltip e.target.id, m.view.chart

  clickPoint: (e) =>
    application.charts.addFrame e.point.id
    for m in application.charts.models
      #if point.series.chart.container.parentElement.id != m.id
      if m.view.chart._c.get
        p = m.view.chart._c.get e.point.id
        if p && p.update
          if p.marker && p.marker.radius > 2
            #p.update({ marker: {}},true)
          else
            p.update({ marker: { color: '#BF0B23', radius: 5}},true)
    return false

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
      #@.chart.series[0].setData(dd)
      @.chart.setData(dd)
    else
      #series = @.chart.series[0]
      for d in data
        @.chart.addPoint(@_formatChartPoint(d),true,true)
        #series.addPoint(@_formatChartPoint(d),true,true)
        @.lastupdate = d.data[0]
        application.charts.lastframe = d.frame_id

  _update: (data) =>
    @_drawData data.data.m

  drawChart: (data) =>
    renderData = @getRenderData()
    @.chart = @.chartInit renderData
    if @.chart.realtime
      application.socket.on "message:OLAP/#{renderData.name}/", @_update
      application.socket.emit 'subscribe', 'OLAP/'+renderData.name+'/'
    return

  render: =>
    super()
    $('#chart-container').append @.$el
    @update null,null,true
    this

  chartInit: (cd) ->
    if cd.chartInfo.name.toLowerCase() in ['line', 'bar', 'pie', 'spline', 'area', 'areaspline','column','scatter']
      _l = 'highchart'
      _c = @_dhc cd
    else
      _l = 'custom'
      _c = @_dcc cd
    lib:_l
    _c:_c
    realtime: cd.realtime || false
    type:cd.chartInfo.name.toLowerCase()
    addPoint: (d) =>
      if @.chart.lib == 'highchart'
        series = @.chart._c.series[0]
        series.addPoint(d,true,true)
      else
        @.chart._c.addPoint(d)
        @.chart._c.render($('#'+@.anchorId))

    setData: (d) =>
      if @.chart.lib == 'highchart'
        @.chart._c.series[0].setData(d)
      else
        @.chart._c.setData(d)
        @.chart._c.render($('#'+@.anchorId))

    showTooltip: (id,me) =>
      if me.lib == 'highchart'
        point = me._c.get id
        if point
          me._c.tooltip.refresh point
        else
          me._c.tooltip.hide()
    hideTooltip:->
      if me.lib == 'highchart'
        me._c.tooltip.hide()

  _dcc: (data) =>
    return new application.charts.customCharts[data.chartInfo.name] data

  _dhc: (data) =>
    renderData = data
    chart = new Highcharts.Chart
      chart:
        renderTo: data.id
        type: renderData.chartInfo.name.toLowerCase()
        height: renderData.chartInfo.height || '150'
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
          #stickyTracking: false
          lineWidth:2
      series: [
        name:renderData.name
        data:[]
        allowPointSelect: true
        shadow:false
        color:renderData.chartInfo.color || 'blue'
        marker:
          enabled: true
          radius: 1
        ]
      tooltip:
        snap:100
        crosshairs:true
        #enabled:false
      #  headerFormat:
      #    ''
      #  pointFormat:
      #    '<small>{point.z}</small><br><b>{point.y}% movement</b>'
      #animation:
      #  duration:
      #    1000
      xAxis:
        tickInterval: renderData.chartInfo.tickerinterval * 1000 || null
        type:
          renderData.chartInfo.xtype || 'datetime'
        labels:
          formatter: -> 
            if this.axis.options.type == 'datetime'
              Highcharts.dateFormat('%m/%d<br>%I:%M:%S', this.value)
            else
              this.value /1000
      yAxis:
        title:
          text: ''
        min:renderData.chartInfo.minval
        max:renderData.chartInfo.maxval
    return chart
