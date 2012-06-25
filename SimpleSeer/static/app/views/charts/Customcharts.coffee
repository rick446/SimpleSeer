application = require '../../application'
ChartView = require '../chart'

module.exports = class Customcharts extends ChartView
  template: require '../templates/chart'
  initialize:(d) =>
    super d 
    @lib = 'customchart'
    this

  buildChart: =>
    super()
    #super new application.charts.customCharts[data.chartInfo.name] data

  addPoint: (d) =>
    console.log 'add point!'
    super d
    if @.stack
      @.stack.add d
      #@.addPoint(d)
      @.render($('#'+@.anchorId))

  incPoint: (d) =>
    #console.log 'inc point!'
    super d
    return

  setData: (d) =>
    #console.log 'set data!'
    super d
    #@.render()

  render: =>
    super()

  showTooltip: (id) =>
    return

  hideTooltip: =>
    return
   
  alterPoint: (pId, v=0) =>
    super(pId, v)
    #@.alterPoint(pId, v)

