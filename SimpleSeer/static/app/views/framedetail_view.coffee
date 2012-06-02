View = require './view'
template = require './templates/framedetail'
app = require('application')

module.exports = class FrameDetailView extends View  
  template: template

  getRenderData: =>
    data = {}
    
    if @model.get("features")?
      data.featuretypes = _.values(@model.get("features").groupBy (f) -> f.get("featuretype"))
    
    for k of @model.attributes
      data[k] = @model.attributes[k]
      
    data
    
  
  afterRender: =>
    @$(".tablesorter").tablesorter()
