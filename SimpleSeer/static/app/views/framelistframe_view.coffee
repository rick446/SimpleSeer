View = require './view'
template = require './templates/framelistframe'
application = require('application')

module.exports = class FramelistFrameView extends View
  template: template

  events:
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
    html='<tr><td class="item-detail clickEdit"><input type="text"'
    if disabled
      html+=' disabled="disabled" '
    html+='></td><td class="item-detail-value clickEdit"><input type="text"'
    if disabled
      html+=' disabled="disabled" '    
    html+='></td></tr>'
    $(obj).append(html)

  updateMetaData: (self) =>  
    metadata = {}
    
    rows = $(self).find("tr")
    rows.each (id, obj) ->
      tds = $(obj).find('td')
      metadata[$(tds[0]).html()] = $(tds[1]).html()
    
    @addMetaBox(self)
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

    unless target.find("input").length is 0
      target.find("td").each (id, obj) ->
        $(obj).html $(obj).find("input").attr("value")

    @delBlankMeta(target)
    @updateMetaData(target)
    
  initialize: (frame)=>
    super()
    @frame = frame.model

  getRenderData: =>
    capturetime: new Date parseInt @frame.get('capturetime')+'000'
    camera: @frame.get('camera')
    imgfile: @frame.get('imgfile')
    thumbnail_file: @frame.get('thumbnail_file')
    id: @frame.get('id')
    features: @frame.get('features')
    metadata: @frame.get('metadata')
    width: @frame.get('width')
    height: @frame.get('height')
    notes: @frame.get('notes')
  
