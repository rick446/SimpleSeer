Collection = require "./collection"
frameset = require "../models/frameset"
FrameSetView = require '../views/frameset_view'
#application = require '../application'


module.exports = class FrameSets extends Collection
  url: "/api/frameset"
  model: frameset
  
