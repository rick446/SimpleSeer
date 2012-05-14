Collection = require "./collection"
OLAP = require "models/OLAP"

module.exports = class OLAPs extends Collection
  url: "/api/olap"
  model: OLAP