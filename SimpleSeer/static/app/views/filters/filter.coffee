SubView = require '../subview'
application = require '../../application'
ChartView = require '../chart'

module.exports = class _filter extends SubView
  value:null
  initialize: (params) =>
    super()
    _ret = $.ajax '/getFilter/'+@options.params.type+'/'+@options.params.field_name+'/'+@options.params.format, {dataType:'json', async:false}
    @options.params.constraints = $.parseJSON _ret.responseText
    @options.params.name = (@options.params.field_name+'-'+@options.params.format).replace(/[^a-z0-9_\-]/gi,'_')
    #if !@options.parent.filterCallback?
    #  @options.parent.filterCallback: (data) ->
      
    @

  render: () =>
    @options.parent.$(@options.selector).append('<div id="'+@id+'"></div>') 
    @options.selector = '#'+@id
    super()
  
  setValue: (v, send=false) =>
    @value = v
    if send
      @submitQuery()
    
  getValue: () =>
    @value

  toJson: () =>
    false

  submitQuery: () =>
    _json = []
    for i,o of @options.parent.subviews
      val = o.toJson()
      if val
        _json.push val
    #todo: get root url from parent object
    url = "/getFrames/"+JSON.stringify _json
    $.getJSON(url, (data) =>
      @options.parent.filterCallback data
      return
    ).error =>
      #todo: make callback error
      SimpleSeer.alert('request error','error')

