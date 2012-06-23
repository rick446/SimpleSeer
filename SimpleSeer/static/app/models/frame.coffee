Model = require "./model"
Feature = require "models/feature"
FeatureSet = require "../collections/featureset"


module.exports = class Frame extends Model
  urlRoot: "/api/frame"

  parse: (response) =>
    if response.features.length
      response.features = new FeatureSet( (new Feature(f) for f in response.features) )
    
    unless response.thumbnail?
      response.thumbnail = "/grid/thumbnail/" + response.id
    response
