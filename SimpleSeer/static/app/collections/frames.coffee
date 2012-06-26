Collection = require "./collection"
Frame = require "../models/frame"

module.exports = class Frames extends Collection
  url: "/frames"
  model: Frame

  parse: (response)=>
    @total_frames = response.total_frames
    return response.frames

  fetch_filtered: (options)=>
    params =
      filter: JSON.stringify({})
      limit: 20
      skip: 0
      sort: JSON.stringify({'capturetime': -1 })
    if options && options.filter
      if options.filter.time_from || options.filter.time_to
        options.filter.capturetime = {}
        if options.filter.time_from
          options.filter.capturetime['$gte'] = {'$date': options.filter.time_from}
          delete options.filter.time_from
        if options.filter.time_to
          options.filter.capturetime['$lte'] = {'$date': options.filter.time_to}
          delete options.filter.time_to
      params.filter = JSON.stringify(options.filter)
    if options && options.skip
      params.skip = options.skip
    add = params.skip != 0
    if options && options.add
      add = options.add
    fetch_params =
      add: add
      data: params
    if options && options.success
      fetch_params.success = options.success
    @fetch fetch_params