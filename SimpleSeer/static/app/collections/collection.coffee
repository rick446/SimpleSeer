# Base class for all collections.
Backbone = if describe? then require('backbone') else window.Backbone

module.exports = class Collection extends Backbone.Collection
