Model = require './model'
Collection = require './collection'

module.exports = 
  url: "/olap/"

  model: class OLAP extends Model
    default:
      data: []
    
  collection: class OLAPCollection extends Collection
    model: OLAP 
    url: @url
