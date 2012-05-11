Model = require "./model"

module.exports = class Measurement extends Model
  url: -> "/api/measurement"