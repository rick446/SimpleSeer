View = require './view'

#template = require './templates/chart'
view_helper = require '../lib/view_helper'
application = require '../application'

module.exports = class ChartView extends View
  template: ''
  lastframe: ''
  
  initialize: =>
    #todo: find a way to make this work:
    #if @.type == 'ChartView'
    #  console.error 'ChartView is abstract and cannot be instantiated'
    #  return
    @anchorId = @model.id
    @name = @model.name
    @realtime = @model.realtime || false
    @type = @model.name.toLowerCase()
    @accumulate = @model['accumulate'] || false
    @olap = @model.olap
    @color = @model.color
    if @accumulate
      _m = application.charts.get @id
      @stack = _m.pointStack()    
    tf = new moment().utc().subtract('s',application.charts.timeframe).valueOf()
    @update tf,null,true
    this

  setData: (d) =>
    return d
  addPoint: (d) =>
    return d
  incPoint: (d) =>
    return d
  alterPoint: (d) =>
    return d

  buildChart: (c=false) =>
    if c
      @_c = c
    return
  
  afterRender: =>
    # may not need this
    @buildChart()
    #todo: track all subscriptions. If subscribe is already in place, just bind callback, dont re-subscribe
    if @.realtime && application.socket
      application.socket.on "message:Chart/#{@.name}/", @_update
      if !application.subscriptions['Chart/'+@.name+'/']
        application.subscriptions['Chart/'+@.name+'/'] = application.socket.emit 'subscribe', 'Chart/'+@.name+'/'

  getRenderData: =>
    retVal = application.charts.get(@.anchorId)
    if retVal
      return retVal.attributes
    return false

  update: (frm, to, reset=true )=>
    m = application.charts.get(@.anchorId)
    name = m.attributes.name
    if frm and to
      url = "/chart/"+name+"/since/"+frm+"/before/" + to
    else if frm
      url = "/chart/"+name+"/since/" + frm
    else
      console.error 'frm and or to required'
      return false
    $.getJSON(url, (data) =>
      @_drawData( @_clean(data.data), reset)
      #@._drawData data.data,reset
      $('.alert_error').remove()
      return
     ).error =>
       SimpleSeer.alert('Connection lost','error')
  """
  _drawDataLegacy: (data, reset) =>
    if data.length == 0
      return
    dd = []
    for d in data
      dd.push
        data: [d[0], d[1]]
        frame_id: d[3]
    @_drawData dd, reset
  """
  _formatChartPoint: (d) =>
    #todo: push some of this up the abstraction chain
    if !@.model.accumulate
      cp = @.clickPoint
      mo = @.overPoint
    if @.model.xtype == 'datetime'
      d.d[0] = new moment d.d[0]
      #console.log d.d[0]
    if @.model.accumulate
      #if !d.d?
      #  console.dir d
      #  console.trace()
      _id = d.d[1]
    else
      _id = d.m[2]
    _point =
      y:d.d[1]
      x:d.d[0]
      id:_id
      events:
        #click: application.charts.callFrame
        mouseOver: mo
        click: cp
        #unselect: @.unselectPoint #application.charts.removeFrame
    return _point

  overPoint: (e) =>
    if application.charts._imageLoader
      clearInterval application.charts._imageLoader
    application.charts._imageLoader = setTimeout (->
      application.charts.previewImage e.target.id
    ), 500
    for m in application.charts.models
      if !m.attributes.ticker && m.view
        m.view.showTooltip e.target.id

  clickPoint: (e) =>
    application.charts.addFrame e.point.id
    for m in application.charts.models
      #if point.series.chart.container.parentElement.id != m.id
      if m.view._c.get
        p = m.view._c.get e.point.id
        if p && p.update
          if p.marker && p.marker.radius > 2
            #p.update({ marker: {}},true)
          else
            p.update({ marker: { color: '#BF0B23', radius: 5}},true)
    return false

  #todo: move this to setData
  _drawData: (data,reset=false) =>
    dd = []
    if reset
      if @.model.accumulate
        dd = @.stack.buildData data
      else
        dd = data
        #if @.name == 'Delivered Candies by Color' || @.name == 'Candies by Color Green'
        #  console.log data
        #for d in data
          #if @.name == 'Delivered Candies by Color' || @.name == 'Candies by Color Green'
          #  console.log d.d[1]
          #if d.d[1] > 0
            #p = @_formatChartPoint d
            #dd.push p
      #if @olap == 'DeliveredGreen'
      #  console.dir dd
      @.setData dd
    else
      for d in data
        #if @olap == 'DeliveredGreen'
        #  console.log @_formatChartPoint d
        if @.model.accumulate
          #console.dir d
          #console.trace()
          #@.incPoint @_formatChartPoint d
          @.incPoint d
        else
          #@.addPoint(@_formatChartPoint(d),true,true)
          @.addPoint(d,true,true)

  _update: (data) =>
    @_drawData @_clean data.data.m.data

  _clean: (data) =>
    refined = []
    for d in data
      refined.push @_formatChartPoint d
    return refined
    
  render: =>
    super()
    $('#chart-container').append @.$el
    this


