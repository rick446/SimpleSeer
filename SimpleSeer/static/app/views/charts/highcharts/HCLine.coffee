lib = require '../Highcharts'

module.exports = class line extends lib
  
  initialize: (d) =>
    super d
    #todo: make sure base checks that required paramaters are set
    #todo: have base class keep track of lib dependencies
    @lib = 'highcharts'
    #@stack = _pointStack()
    this

  addPoint: (d) =>
    super(d)

  setData: (d) =>
    super(d)
