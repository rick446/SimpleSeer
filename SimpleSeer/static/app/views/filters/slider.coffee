_filter = require './filter'
template = require './templates/slider'
application = require 'application'

module.exports = class SliderFilterView extends _filter
  id: 'slider-filter-view'
  template: template
  enabled: false
  
  initialize: () =>
    super()
    @

  events:
    'click :checkbox' : 'toggleEnabled'

  toggleEnabled: ()=>
    sl = @$el.find("#"+@options.params.name+"_sl")
    if @enabled
      @enabled = false
      sl.slider("disable")
      @setValue('',true)
    else
      @enabled = true
      sl.slider("enable")      
      @setValue(sl.slider("values"),true)

  afterRender: () =>
    @$el.find("#"+@options.params.name+"_sl").slider
      range: true
      min: @options.params.constraints.min
      max: @options.params.constraints.max
      disabled:true
      values: [ @options.params.constraints.min, @options.params.constraints.max ]
      slide: (event, ui) =>
        @$el.find("label").html ui.values[0] + " - " + ui.values[1]
      change: (event, ui) =>
        @setValue(ui.values, true)
    #@setValue [@options.params.constraints.min, @options.params.constraints.max]
    
    $("#amount").val  $("#"+@name+"_sl").slider("values", 0) + " - " + $("#"+@name+"_sl").slider("values", 1)
    super()
      
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
