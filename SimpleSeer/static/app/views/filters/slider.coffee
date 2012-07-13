_filter = require './filter'
template = require './templates/slider'
application = require 'application'

module.exports = class SliderFilterView extends _filter
  id: 'slider-filter-view'
  template: template

  initialize: () =>
    super()
    @

  afterRender: () =>
    @$el.find("#slider-range").slider
      range: true
      min: @options.params.constraints.min
      max: @options.params.constraints.max
      values: [ @options.params.constraints.min, @options.params.constraints.max ]
      slide: (event, ui) =>
        @$el.find("label").html ui.values[0] + " - " + ui.values[1]
      change: (event, ui) =>
        @setValue(ui.values, true)
    #@setValue [@options.params.constraints.min, @options.params.constraints.max]
    
    $("#amount").val  $("#slider-range").slider("values", 0) + " - " + $("#slider-range").slider("values", 1)
      
  getRenderData: () =>
    return @options.params
    
  toJson: () =>
    vals = @getValue()
    if vals
      retVal = 
        type:@options.params.type
        lt:vals[1]
        gt:vals[0]
        name:@options.params.field_name
    retVal
