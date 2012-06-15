View = require './view'

template = require './templates/chart'
view_helper = require '../lib/view_helper'
application = require '../application'

module.exports = class ChartView extends View
  template: template
  lastframe: ''
  
  initialize: =>
    @anchorId = @model.id
    if @model.chartInfo.chartid
      @.template = ()->
        return ''

  getRenderData: =>
    retVal = application.charts.get(@.anchorId)
    if retVal
      return retVal.attributes
    return false

  update: (frm, to, reset=true )=>
    m = application.charts.get(@.anchorId)
    name = m.attributes.name
    if frm and to
      url = "/olap/"+name+"/since/"+frm+"/before/" + to
    else if frm
      url = "/olap/"+name+"/since/" + frm
    else
      console.error 'frm and or to required'
      #interval = application.settings.poll_interval || 1
      #url = "/olap/"+name+"/limit/"+Math.ceil(application.charts.timeframe / interval)
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
    if !@.model.chartInfo.accumulate
      cp = @.clickPoint
      mo = @.overPoint
    if @.model.chartInfo.xtype == 'datetime'
      d.data[0] = moment(d.data[0]*1000)
    if @.model.chartInfo.accumulate
      _id = d.data[1]
    else
      _id =d.frame_id
    _point =
      y:d.data[1]
      x:d.data[0]
      id:_id
      events:
        #click: application.charts.callFrame
        mouseOver: mo
        click: cp
        #unselect: @.unselectPoint #application.charts.removeFrame

  overPoint: (e) =>
    if application.charts._imageLoader
      clearInterval application.charts._imageLoader
    application.charts._imageLoader = setTimeout (->
      application.charts.previewImage e.target.id
    ), 500
    for m in application.charts.models
      if !m.attributes.chartInfo.ticker && m.view.chart
        m.view.chart.showTooltip e.target.id

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
      if @.model.chartInfo.accumulate
        dd = @.chart.stack.buildData data
      else
        for d in data
          p = @_formatChartPoint d
          dd.push p
        application.charts.lastframe = d.frame_id
      @.chart.setData(dd)
    else
      for d in data
        if @.model.chartInfo.accumulate
          @.chart.incPoint @_formatChartPoint d 
        else
          @.chart.addPoint(@_formatChartPoint(d),true,true)
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
    tf = Math.round((new Date()).getTime() / 1000) - application.charts.timeframe
    @update tf,null,true
    this

  createSeries: (cd) =>
    id:cd.id
    name:cd.name
    shadow:false
    color:cd.chartInfo.color || 'blue'
    marker:
      enabled: true
      radius: 1

  chartInit: (cd) ->
    _m = application.charts.get @.model.id 
    if cd.chartInfo.name.toLowerCase() in ['line', 'bar', 'pie', 'spline', 'area', 'areaspline','column','scatter']
      _l = 'highchart'
      if cd.chartInfo.chartid
        m = application.charts.get cd.chartInfo.chartid
        m.view.chart._c.addSeries @createSeries cd
        _c = m.view.chart._c
      else
        _c = @_dhc cd
    else
      _l = 'custom'
      _c = @_dcc cd
    if cd.chartInfo.accumulate
      _s =  _m.pointStack()
    else
      _s = false
    stack:_s
    lib:_l
    _c:_c
    name: cd.name
    realtime: cd.realtime || false
    type:cd.chartInfo.name.toLowerCase()
    incPoint: (d) =>
      if @.chart.lib == 'highchart'
        #p = @.chart._c.get d.id
        if @.chart.stack
          d.y = 1
          ep = @.chart.stack.add d
          dd = @.chart.stack.buildData()
          @.chart.setData(dd)
        return

        if p
          p.update(++p.y)
        else
          d.y = 1
          #@.chart.addPoint d
          series = @.chart._c.get @.id
          series.addPoint d
          p = d
      else
        @.chart._c.incPoint(d)
      if @.chart.stack
        ep = @.chart.stack.add p
    addPoint: (d) =>
      console.log d
      if @.chart.stack
        @.chart.stack.add d
      if @.chart.lib == 'highchart'
        series = @.chart._c.get @.id
        series.addPoint(d,true,true)
      else
        @.chart._c.addPoint(d)
        @.chart._c.render($('#'+@.anchorId))

    alterPoint: (pId, v=0) =>
      if @.chart.lib == 'highchart'
        p = @.chart._c.get(pId)
        if p
          if v <= 0
            v = ++p.y
          p.update(v)
      else
        @.chart._c.alterPoint(pId, v)

    setData: (d) =>
      if @.chart.lib == 'highchart'
        series = @.chart._c.get @.id
        series.setData(d)
      else
        @.chart._c.setData(d)
        @.chart._c.render($('#'+@.anchorId))

    showTooltip: (id) ->
      if @.lib == 'highchart'
        point = @._c.get id
        if point
          @._c.tooltip.refresh point
        else
          @._c.tooltip.hide()
    hideTooltip:->
      if @.lib == 'highchart'
        @._c.tooltip.hide()

  _dcc: (data) =>
    return new application.charts.customCharts[data.chartInfo.name] data

  _dhc: (renderData) =>
    _target = $('#'+renderData.id+' .graph-container')
    
    if renderData.chartInfo.ticker
      enableTooltip = false
    chart = new Highcharts.Chart
      chart:
        renderTo: _target[0]
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
      series: [ @createSeries renderData ]
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
              m =  application.charts.get @.chart.id
              if m.attributes.chartInfo.map
                return m.attributes.chartInfo.map[this.value]
              else
                return this.value
      yAxis:
        title:
          text: ''
        min:renderData.chartInfo.minval
        max:renderData.chartInfo.maxval
    chart.id = renderData.id
    return chart
