Collection = require "./collection"
Frame = require "../models/frame"

module.exports = class Frames extends Collection
  url: "/lastframes"
  model: Frame

  parse: (response)=>
    @total_frames = response.total_frames
    return response.frames