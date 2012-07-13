SubView = require '../subview'
application = require '../../application'
ChartView = require '../chart'

module.exports = class _filter extends SubView
  constraints = null
  initialize: (params) =>
    super()
    _ret = $.ajax '/getFilter/'+@options.params.type+'/'+@options.params.field_name+'/'+@options.params.format, {dataType:'json', async:false}
    @constraints = $.parseJSON _ret.responseText
    @options.params.name = (@options.params.field_name+'-'+@options.params.format).replace(/[^a-z0-9_\-]/gi,'_')
    @

  render: () =>
    @options.parent.$(@options.selector).append('<div id="'+@id+'"></div>') 
    @options.selector = '#'+@id
    super()
