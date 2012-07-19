_filter = require './filter'
template = require './templates/autofill'
application = require 'application'

module.exports = class AutofillFilterView extends _filter
  id: 'autofill-filter-view'
  className:'filter_widget'
  template: template

  initialize: () =>
    super()
    @

  setValue: (v, send=false) =>
    if v == '_'
      v = ''
    super(v,send)

  afterRender: () =>
    #$( "#combobox" ).combobox();
    
    @$el.find('#'+@options.params.name+'_af').combobox
      selected: (event, ui) =>
        if ui.item
          v = ui.item.value
        @setValue(v, true)
      width:"50px"
    super()

  getRenderData: () =>
    return @options.params

  toJson: () =>
    val = @getValue()
    if val
      retVal = 
        type:@options.params.type
        eq:@getValue()
        name:@options.params.field_name
    retVal
