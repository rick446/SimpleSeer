View = require './view'
template = require './templates/framelistframe'
application = require('application')

module.exports = class FramelistFrameView extends View
  template: template
  
  initialize: (frame)=>
    super()
    for k in application.settings.ui_metadata_keys
      if !frame.model.attributes.metadata[k]?
        frame.model.attributes.metadata[k] = ''
    @frame = frame.model

  
  events:
    'click .action-viewFrame' : 'expandImage'
    'keypress .action-viewFrame' : 'expandImage'
    'click .clickEdit'  : 'switchStaticMeta'
    'blur .clickEdit'  : 'switchInputMeta'
    'click .notes-field' : 'setDirty'
    'change .notes-field' : 'updateNotes'
    'click .savebtn' : 'setSaved'
    'focus .ivi-right' : 'showSaved'
    'blur .ivi-right' : 'hideSaved'

  expandImage: =>
    application.framelistView.showImageExpanded @$el, @frame, @model
    @$el.find('.featureLabel').show()
    
  hideImage: =>
    @$el.find('.featureLabel').hide()

  showSaved: =>
    @$el.find('.savebtn').show()
    
  hideSaved: =>
    @$el.find('.savebtn').hide()
    
  setSaved: =>
    @$el.find('.savebtn').button( "option" , 'label' , 'Saved' )
    @$el.find('.savebtn').button('disable')
    
  setDirty: =>
    @$el.find('.savebtn').button('enable')
    @$el.find('.savebtn').button( "option" , 'label' , 'Save' )
    @$el.find('.savebtn').show()

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
    @setSaved()

  updateNotes: (e) =>
    @model.save {notes:$(".notes-field").attr('value')}
    @setSaved()

  switchStaticMeta: (e) =>
    self = $(e.currentTarget)
    @setDirty()

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
      capturetime: new moment(parseInt @frame.get('capturetime')+'000').format("M/D/YYYY h:mm a")
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
    @$el.find(".notes-field").autogrow()
    @$el.find('.savebtn').button()
    @$el.find('.savebtn').hide()
    @setSaved()
    
  renderTableRow: (table) =>
    awesomeRow = []
    rd = @getRenderData()
    awesomeRow['Capture Time'] = rd.capturetime
    for i in rd.metadata
      awesomeRow[i.key] = i.val
    if rd.features.models
      f = rd.features.models[0].getPluginMethod(rd.features.models[0].get("featuretype"), 'metadata')()
    else
      f = {}
    pairs = {}
    for i,o of f
      awesomeRow[o.title + o.units] = o.value
    table.addRow(awesomeRow)

  
