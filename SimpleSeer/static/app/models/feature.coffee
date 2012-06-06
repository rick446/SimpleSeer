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
      
  name: =>
    plugin = @getPluginMethod(@.get("name"), 'tableData')
    if plugin?
      return plugin()
    return @.get("featuretype").replace("Feature","")
    
  plural: =>
    plugin = @getPluginMethod(@.get("plural"), 'tableData')
    if plugin?
      return plugin()
    return @name() + "s"
  
  icon: =>
    plugin = @getPluginMethod(@.get("icon"), 'tableData')
    if plugin?
      return plugin()
    return ""
  
  render: (pjs) =>
    plugin = @getPluginMethod(@.get("featuretype"), 'render')
    if plugin?
      return plugin(pjs)
    pjs.stroke 0, 180, 180
    pjs.strokeWeight 3
    pjs.noFill()
    pjs.rect @.get('x')-@.get('width')/2,@.get('y')-@.get('height')/2,@.get('width'),@.get('height')
    
