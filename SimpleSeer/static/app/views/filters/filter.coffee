SubView = require '../subview'
application = require '../../application'
ChartView = require '../chart'

module.exports = class _filter extends SubView
  value:null
  className:'filter_widget'
  initialize: () =>
    super()
    @collection = @options.collection || null
    _ret = $.ajax '/getFilter/'+@options.params.type+'/'+@options.params.field_name+'/'+@options.params.format, {dataType:'json', async:false}
    @options.params.constraints = $.parseJSON _ret.responseText
    @options.params.name = (@options.params.field_name+'-'+@options.params.format).replace(/[^a-z0-9_\-]/gi,'_')
    @

  render: () =>
    @options.parent.$(@options.selector).append('<div id="'+@id+'"></div>') 
    @options.selector = '#'+@id
    super()
  
  afterRender: ()=>
    @$el.addClass(@className)
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

      
