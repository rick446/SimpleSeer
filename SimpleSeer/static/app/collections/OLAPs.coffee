Collection = require "./collection"
OLAP = require "models/OLAP"

module.exports = class OLAPs extends Collection
  url: "/api/olaps"
  model: OLAP