require 'lib/view_helper'
require 'views/view'

module.exports = class SubView extends View
  options:
    parent: null
    selector: null

  render: () =>
    @setElement @options.parent.$ @options.selector
    # Do other render-fu
    @