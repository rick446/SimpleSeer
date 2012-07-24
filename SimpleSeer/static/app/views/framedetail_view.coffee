View = require './view'
template = require './templates/framedetail'
application = require('application')

module.exports = class FrameDetailView extends View  
  template: template
  
  events:
    'change .metaDataEdit' : 'updateMetaData'
    'change .notesEdit' : 'updateNotes'
    
  zoom: (e, ui) ->
    scale = $("#zoomer").data("orig-scale")
    os = $('#display').offset()
    viewPort = $('#display-zoom')

    # The image is already scaled, factor that in.
    ui.zoom = scale * ui.zoom
    
    if ui.zoom is 1
      @zoomed = false
      viewPort.css({
        'position': 'static',
        'left': 0,
        'top': 0,
        'width': '100%',
        'height': '100%'
      });
    else
      @zoomed = true
      viewPort.css({
        'position': 'relative',
        'top': '-'+(@.model.attributes.height * ui.zoom * ui.y)+'px',
        'left': '-'+(@.model.attributes.width * ui.zoom * ui.x)+'px',
        'width': (@.model.attributes.width * ui.zoom)+'px',
        'height': (@.model.attributes.height * ui.zoom)+'px',
      });
      $('#display').css("height", (@.model.attributes.height * scale))
      

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
    @addMetaBox()
    
    framewidth = @model.get("width")
    realwidth = $('#display-img').width()
    scale = realwidth / framewidth

    $("#zoomer").zoomify({
      image: @model.get('imgfile'),
      zoom: 1,
      update: (e, ui) =>
        @zoom(e, ui)
    }).data("orig-scale", scale);
    
    if not @model.get('features').length
      return
      
    @$(".tablesorter").tablesorter()
    @pjs = new Processing("displaycanvas")
    @pjs.background(0,0)
    @pjs.size $('#display-img').width(), @model.get("height") * scale
    @pjs.scale scale
    @model.get('features').each (f) => f.render(@pjs)
