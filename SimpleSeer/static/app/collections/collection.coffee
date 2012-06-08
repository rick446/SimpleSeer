# Base class for all collections.
Backbone = if describe? then require('backbone') else window.Backbone

module.exports = class Collection extends Backbone.Collection
  ajaxTried: 0

  sync: =>
    args = arguments
    Backbone.sync.apply( this, args )
    .done =>
      @ajaxTried = 0
    .fail =>
      if @ajaxTried < 3
        @ajaxTried = @ajaxTried+1
        @sync.apply( this, args )
      else
        @ajaxTried = 0
        $('#lost_connection').dialog 'open'
