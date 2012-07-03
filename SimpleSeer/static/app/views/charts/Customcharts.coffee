application = require '../../application'
ChartView = require '../chart'

module.exports = class Customcharts extends ChartView
  template: require '../templates/chart'
  initialize:(d) =>
    #@.$el = $ "<div/>", id: @id
    @lib = 'customchart'
    _m = application.charts.get @id
    @stack = _m.pointStack()
    super d
    this

  buildChart: =>
    super()
    #super new application.charts.customCharts[data.chartInfo.name] data

  addPoint: (d) =>
    #console.log 'add'
    super d
    if @.stack
      @.stack.add d, false
      @.update()


  incPoint: (d) =>
    console.log 'inc'
    super d
    #if @.stack
    #  ep = @.stack.add d false
    @.render($('#'+@.anchorId))

    return

  setData: (d) =>
    console.log 'set'
    super d
    if @.stack
      for _d in d
        #console.log _d
        @.stack.add _d, false
    @.update()

  render: =>
    super()

  showTooltip: (id) =>
    return

  hideTooltip: =>
    return
   
  alterPoint: (pId, v=0) =>
    super(pId, v)
    #@.alterPoint(pId, v)

