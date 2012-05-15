Collection = require "./collection"
Frame = require "models/frame"

module.exports = class Frames extends Collection
  url: "/lastframes"
  model: Frame