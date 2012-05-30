Model = require "./model"

module.exports = class Measurement extends Model
  urlRoot: -> "/api/measurement"
