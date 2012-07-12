application = require '../../application'
ChartView = require '../chart'

module.exports = class HighchartsLib extends ChartView
  stacked = false
  template: require '../templates/chart'
  initialize:(d) =>
    @lib = 'highcharts'
    super d
    this

  buildChart: () =>
    if @model.chartid
      @template = ''
      @$el.html ''
      m = application.charts.get @model.chartid
      m.view._c.addSeries @createSeries()
      chart = m.view._c
    else
      _target = @.$el.find '.graph-container'
      chart = new Highcharts.Chart
        chart:
          renderTo: _target[0]
          type: @model.style.toLowerCase()
          height: @model.height || '150'
        series: [ @createSeries() ]
        xAxis:
          tickInterval: @model.tickerinterval * 1000 || null
          type:
            @model.xtype || 'linear'
          title:
            text: @model.xTitle
          labels:
            formatter: -> 
              if this.axis.options.type == 'datetime'
                Highcharts.dateFormat('%m/%d<br>%I:%M:%S', this.value)
              else
                m = application.charts.get @.chart.id
                if m.attributes.labelmap && m.attributes.labelmap[this.value]
                  return m.attributes.labelmap[this.value]
                else
                  return this.value
        yAxis:
          title:
            text: @model.yTitle
          min:@model.minval
          max:@model.maxval
      chart.id = @id
      if @model.useLabels
        chart.xAxis[0].setCategories @model.labelmap
      super chart

  setStackPoints: (d=false) =>
    if @stacked == true || @_c.series.length > 1
      @stacked=true
      @stackPoints = []
      for i,s of @_c.series
        l = s.data.length
        p = s.data[--l]
        if d && d.x > p.x
          p.x = d.x
          s.addPoint(p, false,true)
        @stackPoints[i] = p

  addPoint: (d,redraw=true,shift=false) =>
    super(d)
    if @.stack
      @.stack.add d
    else
      series = @._c.get @.id
      series.addPoint(d,false,shift)
    @setStackPoints(d)
    if redraw
      series.chart.redraw();

  setData: (d) =>
    super(d)
    @setStackPoints()
    series = @._c.get @.id
    #series.setData([])
    #for _d in d
    #  @.addPoint(_d, false, false)
    #@_c.redraw()
    series.setData(d)
    
  showTooltip: (id) =>
    point = @._c.get id
    if point
      @._c.tooltip.refresh point
    else
      @._c.tooltip.hide()

  hideTooltip: =>
    @._c.tooltip.hide()
    
  alterPoint: (pId, v=0) =>
    super(pId, v)
    p = @._c.get(pId)
    if p
      if v <= 0
        v = ++p.y
      p.update(v)

  incPoint: (d) =>
    #todo: refactor so we dont re-draw chart
    #p = @._c.get d.id
    d.y = 1
    super d
    if @.stack
      @stack.add d
      dd = @.stack.buildData()
      @.setData(dd)
    return

  createSeries: =>
    id:@id
    name:@name
    shadow:false
    color:@color || 'blue'
    marker:
      enabled: true
      radius: 2
    data:[]
    
  isStacked: =>
    return @._c.series.length > 1 ? true : false
