Collection = require "./collection"
application = require '../application'
Frame = require "../models/frame"

module.exports = class FilterCollection extends Collection
  model: Frame

  initialize: (params) =>
    super()
    @filters = []
    if params.view
      @view = params.view
    #todo: map filter sets to view type
    for o in application.settings.ui_filters_framemetadata
      @filters.push @view.addSubview o.format, application.getFilter(o.format), '#filter_form', {params:o,collection:@}
    @

  fetch: (params={}) =>
    #todo: map .error to params.error
    _json = []
    for o in @filters
      val = o.toJson()
      if val
        _json.push val
    #todo: get root url from collection
    #skip = 20 limit = 10 query = []
    _json = {skip:0,limit:0,query:_json}
    url = "/getFrames/"+JSON.stringify _json
    $.getJSON(url, (data) =>
      #@view.filterCallback data
      @reset data.frames
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
