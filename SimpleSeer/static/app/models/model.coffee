# Base class for all models.
Backbone = if describe? then require('backbone') else window.Backbone

module.exports = class Model extends Backbone.Model
