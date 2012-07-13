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
    console.log @options.params.name
    @$el.find('#'+@options.params.name).autocomplete({source: @constraints.enum})
      
  getRenderData: () =>
    return @options.params
