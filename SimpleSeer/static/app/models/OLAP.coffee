Model = require "./model"

module.exports = class OLAP extends Model
  urlRoot: -> "/api/olap"
