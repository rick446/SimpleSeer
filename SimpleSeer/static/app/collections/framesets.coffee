Collection = require "./collection"
frameset = require "../models/frameset"
#ChartView = require '../views/chart'
#application = require '../application'


module.exports = class FrameSets extends Collection
  url: "/api/frameset"
  model: frameset
