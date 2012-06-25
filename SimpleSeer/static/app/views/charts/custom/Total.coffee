ChartView = require '../Customcharts'

module.exports = class total extends ChartView
  
  initialize: (d) =>
    super d
    lib:'custom'
    this

  addPoint: (d) =>
    super(d)
    console.log 'adding point'

  setData: (d) =>
    super(d)
    console.log 'setting data'
