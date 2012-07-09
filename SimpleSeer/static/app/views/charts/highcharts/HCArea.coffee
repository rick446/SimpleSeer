lib = require '../Highcharts'

module.exports = class area extends lib
  
  initialize: (d) =>
    super d
    @lib = 'highcharts'
    this

  addPoint: (d) =>
    super(d)
    
  setData: (d) =>
    super(d)

