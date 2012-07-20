View = require './view'
template = require './templates/framedetail'
application = require('application')

module.exports = class FrameDetailView extends View  
  template: template
  
  events:
    'click #display-zoom' : 'zoom'
    'change .metaDataEdit' : 'updateMetaData'
    'change .notesEdit' : 'updateNotes'
    
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
      _ratio = (@.model.attributes.width / viewPort.width()).toFixed(2);
      if _ratio > 1
        @zoomed = true
        viewPort.css('position', 'relative')
        _top = ((e.pageY * _ratio) - (os.top * _ratio))
        _left = ((e.pageX * _ratio) - (os.left * _ratio))
        _left -= _left / _ratio
        _top -= _top / _ratio
        viewPort.css('top', '-'+_top+'px')
        viewPort.css('left', '-'+_left+'px')
        viewPort.css('width', @.model.attributes.width+'px')
        viewPort.css('height', @.model.attributes.height+'px')

  getRenderData: =>
    data = {}
    if @model.get("features").length
      data.featuretypes = _.values(@model.get("features").groupBy (f) -> f.get("featuretype"))
    
    for k of @model.attributes
      data[k] = @model.attributes[k]
    data.disabled = application.settings.mongo.is_slave || false
    data
    
  addMetaBox: =>
    disabled = application.settings.mongo.is_slave || false
    html='<tr><td><input class="metaDataEdit" type="text"'
    if disabled
      html+=' disabled="disabled" '
    html+='></td><td><input class="metaDataEdit" type="text"'
    if disabled
      html+=' disabled="disabled" '    
    html+='></td></tr>'
    $('#metadata').append(html)

  updateMetaData: (e) =>
    metadata = {}
    _add = true
    $("#metadata tr").each (ind,obj) ->
      tds = $(obj).find('td')
      if $(tds[0]).find('input').attr('value')
        metadata[$(tds[0]).find('input').attr('value')] = $(tds[1]).find('input').attr('value')
      else if $(tds[0]).find('input').attr('value') == '' && $(tds[1]).find('input').attr('value') == ''
        $(obj).remove()
    if _add
      @addMetaBox()
    @.model.save {metadata: metadata}

  updateNotes: (e) =>
    @model.save {notes:$("#notesEdit").attr('value')}
  
      
  postRender: =>
    #application.viewPort = $('#display')
    @addMetaBox()
    if not @model.get('features').length
      return
    @$(".tablesorter").tablesorter()
    @pjs = new Processing("displaycanvas")

    @pjs.background(0,0)
    framewidth = @model.get("width")
    realwidth = $('#display-img').width()
    scale = realwidth / framewidth
        
    @pjs.size $('#display-img').width(), @model.get("height") * scale
    @pjs.scale scale
    @model.get('features').each (f) => f.render(@pjs)
