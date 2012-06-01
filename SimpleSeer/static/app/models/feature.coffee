Model = require "./model"


module.exports = class Feature extends Model

  represent: =>
    plugin = @getPlugin(@.get("featuretype"))
    if plugin and plugin.represent?
      return plugin.represent()
    featuretype + " Feature at (" + @x + "," + @y + ")"
