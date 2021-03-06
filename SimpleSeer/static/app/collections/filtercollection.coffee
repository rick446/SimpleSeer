Collection = require "./collection"
application = require '../application'
Frame = require "../models/frame"
#FramelistFrameView = require './framelistframe_view'

module.exports = class FilterCollection extends Collection
  model: Frame
  url:"/getFrames"
  _defaults:
    skip:0
    limit:20
  skip:0
  limit:20
  sortParams:
    sortkey:''
    sortorder:''
    sorttype:''
  
  initialize: (params) =>
    super()
    @filters = []
    if !application.settings.ui_filters_framemetadata?
      application.settings.ui_filters_framemetadata = []
    if params.view
      @view = params.view
    #todo: map filter sets to view type
    for o in application.settings.ui_filters_framemetadata
      @filters.push @view.addSubview o.field_name, application.getFilter(o.format), '#filter_form', {params:o,collection:@}
    @

  #comparator: (chapter) =>
  #  return -chapter.get("capturetime")
  #  return chapter.get("capturetime")
  
  sortList: (sorttype, sortkey, sortorder) =>
    for o in @filters
      if o.options.params.field_name == sortkey
        @sortParams.sortkey = sortkey
        @sortParams.sortorder = sortorder
        @sortParams.sorttype = sorttype
    return
    
  getUrl: (total=false, addParams)=>
    #todo: map .error to params.error
    _json = []
    for o in @filters
      val = o.toJson()
      if val
        _json.push val
    if total
      skip = 0
      limit = @skip+@limit
    else
      skip=@skip
      limit=@limit
    _json =
      skip:skip
      limit:limit
      query:_json
      sortkey: @sortParams.sortkey || 'capturetime'
      sortorder: @sortParams.sortorder || -1
      sortinfo:
        type: @sortParams.sorttype || ''
        name: @sortParams.sortkey || 'capturetime'
        order: @sortParams.sortorder || -1
    if addParams
      _json = _.extend _json, addParams
    "/"+JSON.stringify _json

  fetch: (params={}) =>
    #console.dir _json
    if params.before
      params.before()
    $.getJSON(@url+@getUrl(), (data) =>
      @.totalavail = data.total_frames
      if @skip == 0
        @reset data.frames
      else
        @add data.frames
      if params.success
        params.success(data)
      return
    ).error =>
      #todo: make callback error
      SimpleSeer.alert('request error','error')


  #filterCallback: (data) =>
    #@reset data.frames
    #for att in data.frames
    #  @add att
