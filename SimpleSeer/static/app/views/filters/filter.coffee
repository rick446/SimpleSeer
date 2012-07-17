SubView = require '../subview'
application = require '../../application'
ChartView = require '../chart'

module.exports = class _filter extends SubView
  value:null
  initialize: () =>
    super()
    @collection = @options.collection || null
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
    @collection.skip = @collection._defaults.skip
    @collection.limit = @collection._defaults.limit
    
    if v == ''
      v = null
    @value = v
    if send
      @collection.fetch()
    
  getValue: () =>
    @value

  toJson: () =>
    false

      
