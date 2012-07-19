_filter = require './filter'
template = require './templates/datetime'
application = require 'application'

module.exports = class DateTimeFilterView extends _filter
  id: 'datetime-filter-view'
  template: template
  _vals:[]

  initialize: () =>
    super()
    tf = new moment(@options.params.constraints.min)
    @options.params.constraints.min = tf
    @options.params.constraints.max = new moment(@options.params.constraints.max)
    @_vals['from'] = tf.valueOf()
    @

  afterRender: () =>
    tf = @$el.find('input[name=time_from]').datetimepicker {timeFormat: 'hh:mm:ss', onClose: @setValue}
    tt = @$el.find('input[name=time_to]').datetimepicker {timeFormat: 'hh:mm:ss', onClose: @setValue}
    tf.datepicker( "setDate",  new Date(@options.params.constraints.min))
    tt.datepicker( "setDate",  new Date(@options.params.constraints.max))
    #console.log @options.params.constraints
    super()

    
  setValue :(e,u) =>
    #todo: check that e is valid dt
    dt = new moment(e)
    id = u.id.replace(@options.params.name,'')
    #v = dt.valueOf()
    """
    if id == 'to'
      if @_vals['to'] < @_vals['from']
        SimpleSeer.alert('Invalid DT sett\'n','dterror')
    else if id == 'from'
      if @_vals['to'] < @_vals['from']
        SimpleSeer.alert('Invalid DT sett\'n','dterror')
    else
      return
    """
    @_vals[id] = dt.valueOf()
    if @_vals['to']? && @_vals['from']?
      super([@_vals['from'],@_vals['to']],true)
      

  getRenderData: () =>
    return @options.params
    
  toJson: () =>
    vals = @getValue()
    if vals
      retVal = 
        type:@options.params.type
        lt:vals[1]
        gt:vals[0]
        name:@options.params.field_name
    retVal
