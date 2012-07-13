_filter = require './filter'
template = require './templates/datetime'
application = require 'application'

module.exports = class DateTimeFilterView extends _filter
  id: 'datetime-filter-view'
  template: template

  initialize: () =>
    super()
    @options.params.constraints.min = new moment(@options.params.constraints.min)
    @options.params.constraints.max = new moment(@options.params.constraints.max)
    @

  afterRender: () =>
    #console.log @options.params.constraints
      
  getRenderData: () =>
    return @options.params
