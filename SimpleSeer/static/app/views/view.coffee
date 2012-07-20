require '../lib/view_helper'

Backbone = if describe? then require('backbone') else window.Backbone

# Base class for all views.
module.exports = class View extends Backbone.View
  subviews: null

  initialize: =>
    super()
    @subviews = {}

  template: =>
    return

  getRenderData: =>
    return

  render: =>
    # console.debug "Rendering #{@constructor.name}"
    @$el.html @template @getRenderData()
    @renderSubviews()
    @afterRender()
    this

  afterRender: =>
    return

  renderSubviews: =>
    for name, subview of @subviews
      subview.render()

  #@view.addSubview o.format, application.getFilter(o.format), '#filter_form', {params:o,collection:@}
  addSubview: (name, viewClass, selector, options, subselector) =>
    options = options or {}
    _.extend options,
      parent:@
      selector:selector
      subselector:subselector
    @subviews[name] = new viewClass(options)
