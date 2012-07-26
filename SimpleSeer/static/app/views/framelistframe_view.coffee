View = require './view'
template = require './templates/framelistframe'


application = require('application')

module.exports = class FramelistFrameView extends View
  template: template
  sideBarOpen: application.settings.showMenu
  
  initialize: (frame)=>
    super()
    for k in application.settings.ui_metadata_keys
      if !frame.model.attributes.metadata[k]?
        frame.model.attributes.metadata[k] = ''
    @frame = frame.model

  
  events:
    'click .action-viewFrame' : 'showImageExpanded'
    'click .clickEdit'  : 'switchStaticMeta'
    'blur .clickEdit'  : 'switchInputMeta'
    'change .notes-field' : 'updateNotes'

  delBlankMeta: (obj) =>
    $(obj).find("tr").each (id, obj) ->
      tds = $(obj).find('td')
      if $(tds[0]).html() == '' && $(tds[1]).html() == ''  
        $(obj).remove()
      
  addMetaBox: (obj) =>
    disabled = application.settings.mongo.is_slave || false
    html='<tr><td class="item-detail"><input type="text"'
    if disabled
      html+=' disabled="disabled" '
    html+='></td><td class="item-detail-value"><input type="text"'
    if disabled
      html+=' disabled="disabled" '    
    html+='></td></tr>'
    $(obj).append(html)

  updateMetaData: (self) =>  
    metadata = {}
    
    rows = $(self).find("tr")
    rows.each (id, obj) ->
      tds = $(obj).find('td')
      input = $(tds[1]).find('input')
      span = $(tds[0]).find('span')
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
    
  getRenderData: =>
    md = @frame.get('metadata')
    metadata = []
    for i in application.settings.ui_metadata_keys
      metadata.push {key:i,val:md[i]}
    retVal =
      capturetime: new moment(parseInt @frame.get('capturetime')+'000').utc().format("M/D/YYYY h:mm a (UTC)")
      camera: @frame.get('camera')
      imgfile: @frame.get('imgfile')
      thumbnail_file: @frame.get('thumbnail_file')
      id: @frame.get('id')
      features: @frame.get('features')
      metadata: metadata
      width: @frame.get('width')
      height: @frame.get('height')
      notes: @frame.get('notes')
    retVal

  afterRender: =>    
    @$el.find(".notes-field").autogrow();
    
    $("#viewStage").find(".close").click =>
      $("#viewStage").hide();
      if @sideBarOpen
        @showSettingsBar()

  hideSettingsBar: (call) =>
    if application.settings.showMenu is true
      application.settings.showMenu = false
      @sideBarOpen = true
      $('#second-tier-menu').hide("slide", { direction: "left" }, 100)
      $("#stage").animate({'margin-left':'90px'}, 100, call)
    else
      @sideBarOpen = false
      call()

  showSettingsBar: =>
    application.settings.showMenu = true
    $('#second-tier-menu').show("slide", { direction: "left" }, 100)
    $("#stage").animate({'margin-left':'343px'}, 100)  

  showImageExpanded: =>
    @hideSettingsBar =>
      thumbnail = @$el.find(".thumb")
      offsetLeft = thumbnail.offset().left + thumbnail.width() + 35
      offsetTop = thumbnail.offset().top - thumbnail.parents("#views").offset().top + 10
      imgWidth = thumbnail.parents("#views").width() - offsetLeft + 75
      
      $("#displayimage").attr("src", @frame.get('imgfile'));
      $("#viewStage").css({"top": offsetTop + "px", "left": offsetLeft + "px", "width": imgWidth + "px", "display": "block"});

      """
        framewidth = @model.get("width")
        realwidth = $('#displayimage').width()
        scale = realwidth / framewidth

        @pjs = new Processing("#displaycanvas")
        @pjs.background(0,0)
        @pjs.size $('#displayimage').width(), @model.get("height") * scale
        @pjs.scale scale
        @model.get('features').each (f) => f.render(@pjs)
      """

  hideImageExpanded: =>
    $("#viewStage").css({"display": "none"})
    
  renderTableRow: =>
    _empty = "---"
    awesomeRow = []
    rd = @getRenderData()
    row = "<tr>"
    row += "<td>"+rd.capturetime+"</td>"
    awesomeRow['Capture Time'] = rd.capturetime
    for i in rd.metadata
      row += "<td>"+(i.val||_empty)+"</td>"
      awesomeRow[i.key] = i.val
    if rd.features.models
      f = rd.features.models[0].getPluginMethod(rd.features.models[0].get("featuretype"), 'metadata')()
    else
      f = {}
    pairs = {}
    for i,o of f
      pairs[o.title] = o.value
    for i in application.settings.ui_feature_keys
      if pairs[i]
        row += "<td>"+pairs[i]+"</td>"
        awesomeRow[i] = pairs[i]
      else
        row += "<td>"+_empty+"</td>"        
    table.addRow(awesomeRow)
    row = $(row)

  
