Collection = require "./collection"
Measurement = require "models/measurement"

module.exports = class Measurements extends Collection
  url: "/api/measurements"
  model: Measurement