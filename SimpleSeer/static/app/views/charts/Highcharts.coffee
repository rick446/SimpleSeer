application = require '../../application'
ChartView = require '../chart'

module.exports = class HighchartsLib extends ChartView
  template: require '../templates/chart'
  initialize:(d) =>
    @lib = 'highcharts'
    super d
    this

  buildChart: () =>
    if @model.chartid
      #todo : make sure this doesnt clone graphs
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
            @model.xtype || 'datetime'
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
          min:@model.minval
          max:@model.maxval
      chart.id = @id
    super chart

  addPoint: (d,redraw=true,shift=true) =>
    super(d)
    if @.stack
      @.stack.add d
    series = @._c.get @.id
    series.addPoint(d,redraw,shift)

  setData: (d) =>
    super(d)
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
      radius: 1
    data:[]
