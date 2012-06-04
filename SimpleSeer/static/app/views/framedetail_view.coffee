View = require './view'
template = require './templates/framedetail'
app = require('application')

module.exports = class FrameDetailView extends View  
  template: template

  getRenderData: =>
    data = {}
    
    if @model.get("features").length
      data.featuretypes = _.values(@model.get("features").groupBy (f) -> f.get("featuretype"))
    
    for k of @model.attributes
      data[k] = @model.attributes[k]
      
    data
    
  
  postRender: =>
    if not @model.get('features').length
      return
    @$(".tablesorter").tablesorter()
    @pjs = new Processing("displaycanvas")
    @pjs.background(0,0)
    
    framewidth = @model.get("width")
    realwidth = $('#display > img').width()
    scale = realwidth / framewidth
    
    @pjs.size $('#display > img').width(), @model.get("height") * scale
    @pjs.scale scale
    @model.get('features').each (f) => f.render(@pjs) 

    
