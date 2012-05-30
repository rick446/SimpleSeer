View = require './view'
template = require './templates/framedetail'

module.exports = class FrameDetailView extends View  
  template: template

  getRenderData: =>
    @model.attributes
