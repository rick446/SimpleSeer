Model = require "./model"
Feature = require "models/feature"
FeatureSet = require "../collections/featureset"


module.exports = class Frame extends Model
  urlRoot: "/api/frame"
  
  initialize: (response) =>
    if response.features && response.features.length
      response.features = new FeatureSet( (new Feature(f) for f in response.features) )
    
    if not response.thumbnail_file? or not response.thumbnail_file
      response.thumbnail_file = "/grid/thumbnail_file/" + response.id
    @attributes = response
    super()
    @
    
  parse: (response) =>
    if response.features.length
      response.features = new FeatureSet( (new Feature(f) for f in response.features) )
    
    if not response.thumbnail_file? or not response.thumbnail_file
      response.thumbnail_file = "/grid/thumbnail_file/" + response.id
    response
