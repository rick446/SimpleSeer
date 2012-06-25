lib = require '../Highcharts'

module.exports = class scatter extends lib

  initialize: (d) =>
    super d
    @lib = 'highcharts'
    this

  addPoint: (d) =>
    super(d)

  setData: (d) =>
    super(d)
