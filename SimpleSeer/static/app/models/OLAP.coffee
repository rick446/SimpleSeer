Model = require "./model"

module.exports = class OLAP extends Model
  url: -> "/api/olap"