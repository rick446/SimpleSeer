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
    tt = new moment(@options.params.constraints.max)
    @options.params.constraints.min = tf
    @options.params.constraints.max = tt
    @_vals['from'] = tf.valueOf()
    @_vals['to'] = tt.valueOf()
    @

  afterRender: () =>
    tf = @$el.find('input[name=time_from]').datetimepicker {timeFormat: "h:mm tt", onClose: @setValue, ampm:true}
    tt = @$el.find('input[name=time_to]').datetimepicker {timeFormat: "h:mm tt", onClose: @setValue, ampm:true}
    tf.datepicker( "setDate",  new Date(@options.params.constraints.min-application.timeOffset))
    tt.datepicker( "setDate",  new Date(@options.params.constraints.max-application.timeOffset))
    #console.log @options.params.constraints
    super()

    
  #setValue ALWAYS expects a date in the local time
  setValue :(e,u) =>
    dt = new moment(e)
    dt.add('ms',application.timeOffset)
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
