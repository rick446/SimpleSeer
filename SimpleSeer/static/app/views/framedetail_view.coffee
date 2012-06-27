View = require './view'
template = require './templates/framedetail'
app = require('application')

module.exports = class FrameDetailView extends View  
  template: template
  
  events:
    'click #display-zoom' : 'zoom'
    
  zoom: (e) ->
    os = $('#display').offset()
    viewPort = $('#display-zoom')
    if @zoomed
      @zoomed = false
      viewPort.css('position', 'static')
      viewPort.css('left', 0)
      viewPort.css('top', 0)
      viewPort.css('width', '100%')
      viewPort.css('height', '100%')
    else
      @zoomed = true
      viewPort.css('position', 'relative')
      viewPort.css('top', '-'+(e.pageY - os.top)+'px')
      viewPort.css('left', '-'+(e.pageX - os.left)+'px')
      viewPort.css('width', @.model.attributes.width+'px')
      viewPort.css('height', @.model.attributes.height+'px')

  getRenderData: =>
    data = {}
    
    if @model.get("features").length
      data.featuretypes = _.values(@model.get("features").groupBy (f) -> f.get("featuretype"))
    
    for k of @model.attributes
      data[k] = @model.attributes[k]
      
    data
    
  
  postRender: =>
    #app.viewPort = $('#display')
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


    
