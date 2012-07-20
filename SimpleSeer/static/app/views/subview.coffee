require 'lib/view_helper'
View = require './view'

module.exports = class SubView extends View
  options:
    parent: null
    selector: null

  render: () =>
    @setElement @options.parent.$ @options.selector
    super
    @
