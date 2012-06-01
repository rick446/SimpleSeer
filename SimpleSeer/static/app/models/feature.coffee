Model = require "./model"


module.exports = class Feature extends Model

  represent: =>
    plugin = @getPluginMethod(@.get("featuretype"), 'represent')
    if plugin?
      return plugin()
    @.get("featuretype") + " at (" + @.get("x") + "," + @.get("y") + ")"
    
  tableOk: =>
    plugin = @getPluginMethod(@.get("featuretype"), 'tableOk')
    if plugin?
      return plugin()
  
  tableHeader: =>
    plugin = @getPluginMethod(@.get("featuretype"), 'tableHeader')
    if plugin?
      return plugin()
  
  tableData: =>
    plugin = @getPluginMethod(@.get("featuretype"), 'tableData')
    if plugin?
      return plugin()
  
  render: (pjs) =>
    plugin = @getPluginMethod(@.get("featuretype"), 'render')
    if plugin?
      return plugin(pjs)
      
    
