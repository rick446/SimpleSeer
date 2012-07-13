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
      min: @constraints.min
      max: @constraints.max
      values: [ @constraints.min, @constraints.max ]
      slide: (event, ui) ->
        $("#amount").val  ui.values[0] + " - " + ui.values[1]
    
    $("#amount").val  $("#slider-range").slider("values", 0) + " - " + $("#slider-range").slider("values", 1)
    #@$el.find('#'+@options.params.name).autocomplete({source: @constraints.enum})
      
  getRenderData: () =>
    return @options.params
