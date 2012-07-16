_filter = require './filter'
template = require './templates/autofill'
application = require 'application'

module.exports = class AutofillFilterView extends _filter
  id: 'autofill-filter-view'
  template: template

  initialize: () =>
    super()
    @

  afterRender: () =>
    @$el.find('#'+@options.params.name).autocomplete
      source: @options.params.constraints.enum
      change: (event, ui) =>
        if ui.item
          v = ui.item.value
        @setValue(v, true)

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
