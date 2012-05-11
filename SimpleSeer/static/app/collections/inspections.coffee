Collection = require "./collection"
Inspection = require "models/inspection"

module.exports = class Inspections extends Collection
  url: "/api/inspections"
  model: Inspection