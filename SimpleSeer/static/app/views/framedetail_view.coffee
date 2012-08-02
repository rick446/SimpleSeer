View = require './view'
template = require './templates/framedetail'
application = require('application')

module.exports = class FrameDetailView extends View  
  template: template

  initialize: (frame)=>
    super()
    for k in application.settings.ui_metadata_keys
      if !frame.model.attributes.metadata[k]?
        frame.model.attributes.metadata[k] = ''
    @frame = frame.model
  
  events:
    'click #toggleProcessing' : 'togglePro'
    'click .clickEdit'  : 'switchStaticMeta'
    'blur .clickEdit'  : 'switchInputMeta'
    'change .notes-field' : 'updateNotes'
    'resize window': 'updateScale'
    'dblclick #display-zoom': 'clickZoom'

  togglePro: =>
    $("#displaycanvas").toggle();

  clickZoom: (e) ->
    viewPort = $('#display-zoom')
    scale = $("#zoomer").data("orig-scale")
    fakeZoom = Number($("#zoomer").data("last-zoom"))
    fakeZoom += .2

    clickX = e.clientX - 300
    clickY = e.clientY - 48
    
    oldLeft = clickX - Number($("#display-zoom").css("left").replace("px", ""))
    oldTop = clickY - Number($("#display-zoom").css("top").replace("px", ""))
    oldWidth = viewPort.width()
    oldHeight = viewPort.height()

    newWidth = (@.model.attributes.width * fakeZoom)
    newHeight = (@.model.attributes.height * fakeZoom)
    newLeft = oldLeft / oldWidth * newWidth  
    newTop = oldTop / oldHeight * newHeight

    # new point goes in center
    x = Number($("#display-zoom").css("left").replace("px", "")) - (newLeft - oldLeft)
    y = Number($("#display-zoom").css("top").replace("px", "")) - (newTop - oldTop)

    $("#zoomer").zoomify("option", {zoom: Math.floor((fakeZoom*100))/100, x: (-x) / newWidth, y: (-y)/ newHeight})
    $('#display').css("height", (@.model.attributes.height * scale))    
  
  zoom: (e, ui) ->
    scale = $("#zoomer").data("orig-scale")
    os = $('#display').offset()
    viewPort = $('#display-zoom')
    
    viewPort.css({
      'position': 'relative',
      'top': '-'+(@.model.attributes.height * ui.zoom * ui.y)+'px',
      'left': '-'+(@.model.attributes.width * ui.zoom * ui.x)+'px',
      'width': (@.model.attributes.width * ui.zoom)+'px',
      'height': (@.model.attributes.height * ui.zoom)+'px',
    });
    $('#display').css("height", (@.model.attributes.height * scale))

    i = (scale / ui.zoom)

    if ui.zoom != Number($("#zoomer").data("last-zoom"))
      @pjs = new Processing("displaycanvas")
      @pjs.background(0,0)
      @pjs.size $('#display-img').width(), $("#display-img").height()
      @pjs.scale @calculateScale() / i
      if @model.get('features').length then @model.get('features').each (f) => f.render(@pjs)
    
    $("#zoomer").data("last-zoom", ui.zoom)
    
  getRenderData: =>
    data = {}
   
    if @model.get("features").length
      data.featuretypes = _.values(@model.get("features").groupBy (f) -> f.get("featuretype"))
    
    for k of @model.attributes
      data[k] = @model.attributes[k]
    data.disabled = application.settings.mongo.is_slave || false

    md = @frame.get('metadata')
    metadata = []
    for i in application.settings.ui_metadata_keys
      metadata.push {key:i,val:md[i]}
    data.metadata = metadata

    data.capturetime = new moment(parseInt @frame.get('capturetime')+'000').format("M/D/YYYY h:mm a")
  
    data
    
  addMetaBox: =>
    return
    disabled = application.settings.mongo.is_slave || false
    html='<tr><td><input class="metaDataEdit" type="text"'
    if disabled
      html+=' disabled="disabled" '
    html+='></td><td><input class="metaDataEdit" type="text"'
    if disabled
      html+=' disabled="disabled" '    
    html+='></td></tr>'
    $('#metadata').append(html)

  updateMetaData: (self) =>  
    metadata = {}
    
    rows = @$el.find(".editableMeta tr")
    rows.each (id, obj) ->
      tds = $(obj).find('td')
      input = $(tds[0]).find('input')
      span = $(tds[0]).find('span')[0]
      metadata[$(span).html()] = input.attr('value')
    
    #@addMetaBox(self)
    @model.save {metadata: metadata}

  updateNotes: (e) =>
    @model.save {notes:$(".notes-field").attr('value')}

  switchStaticMeta: (e) =>
    self = $(e.currentTarget)

    if self.find("input").length == 0
      $(self).html "<input type=\"text\" value=\"" + self.html() + "\">"
      self.find("input").focus()

  switchInputMeta: (e) =>
    target = $(e.currentTarget).parent().parent()

    #unless target.find("input").length is 0
    #  target.find("td").each (id, obj) ->
    #    $(obj).html $(obj).find("input").attr("value")

    #@delBlankMeta(target)
    @updateMetaData(target)

  calculateScale: =>
    framewidth = @model.get("width")
    realwidth = $('#display').width()
    scale = realwidth / framewidth

    scale

  updateScale: =>
    scale = @calculateScale()
    if scale is $("#zoomer").data("orig-scale")
      return

    fullHeight = $(window).height() - 48
      
    $("#zoomer").data("orig-scale", scale)
    $("#zoomer").zoomify("option", {
      min: (scale.toFixed(2)) * 100,
      max: 400,
      height: (fullHeight / @model.get("height")) / scale,
      zoom: scale.toFixed(2),
    })
  
  postRender: =>
    @addMetaBox()
    scale = @calculateScale()

    fullHeight = $(window).height() - 48;
    $("#zoomer").zoomify({
      image: @model.get('imgfile'),
      y: 25,
      height: (fullHeight / @model.get("height")) / scale,
      min: (scale.toFixed(2)) * 100,
      max: 400,
      zoom: scale.toFixed(2),
      update: (e, ui) =>
        @zoom(e, ui)
    }).data("orig-scale", scale)
        
    if not @model.get('features').length
      return
      
    @$(".tablesorter").tablesorter()
    @pjs = new Processing("displaycanvas")
    @pjs.background(0,0)
    @pjs.size $('#display-img').width(), @model.get("height") * scale
    @pjs.scale scale
    if @model.get('features').length then @model.get('features').each (f) => f.render(@pjs)

    $("#display-zoom").draggable({
      drag: (e, ui) ->
        w0 = $("#frameHolder").width()
        h0 = $("#frameHolder").height()
        w = $("#display-zoom").width()
        h = $("#display-zoom").height()
        
        if ui.position.left > 0
          ui.position.left = 0
          
        if ui.position.top > 0
          ui.position.top = 0
          
        if -1*ui.position.left + w0 > w
          ui.position.left = w0 - w
          
        if -1*ui.position.top + h0 > h
          ui.position.top = h0 - h

        $("#zoomer").zoomify("option", {"x": -1*ui.position.left / w, "y": -1*ui.position.top / h})
    });
    
    @$el.find(".notes-field").autogrow();
