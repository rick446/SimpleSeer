# Put your handlebars.js helpers here.



#logical functions, thanks to
#https://github.com/danharper/Handlebars-Helpers and js2coffee.org
Handlebars.registerHelper "if_eq", (context, options) ->
  return options.fn(context)  if context is options.hash.compare
  options.inverse context

Handlebars.registerHelper "unless_eq", (context, options) ->
  return options.unless(context)  if context is options.hash.compare
  options.fn context

Handlebars.registerHelper "if_gt", (context, options) ->
  return options.fn(context)  if context > options.hash.compare
  options.inverse context

Handlebars.registerHelper "unless_gt", (context, options) ->
  return options.unless(context)  if context > options.hash.compare
  options.fn context

Handlebars.registerHelper "if_lt", (context, options) ->
  return options.fn(context)  if context < options.hash.compare
  options.inverse context

Handlebars.registerHelper "unless_lt", (context, options) ->
  return options.unless(context)  if context < options.hash.compare
  options.fn context

Handlebars.registerHelper "if_gteq", (context, options) ->
  return options.fn(context)  if context >= options.hash.compare
  options.inverse context

Handlebars.registerHelper "unless_gteq", (context, options) ->
  return options.unless(context)  if context >= options.hash.compare
  options.fn context

Handlebars.registerHelper "if_lteq", (context, options) ->
  return options.fn(context)  if context <= options.hash.compare
  options.inverse context

Handlebars.registerHelper "unless_lteq", (context, options) ->
  return options.unless(context)  if context <= options.hash.compare
  options.fn context

Handlebars.registerHelper "nl2br", (text) ->
  nl2br = (text + "").replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, "$1" + "<br>" + "$2")
  new Handlebars.SafeString(nl2br)

Handlebars.registerHelper 'epoch', (epoch) ->
  d = new Date parseInt epoch * 1000
  
  zp = (n) ->
    if n < 10
      n = "0" + n
    n.toString()
  
  (d.getMonth() + 1) + "/" + zp(d.getDate()) + " " + zp(d.getHours()) + ":" + zp(d.getMinutes()) + ":" + zp(d.getSeconds())

Handlebars.registerHelper 'epochtime', (epoch) ->
  d = new Date parseInt epoch * 1000
  
  zp = (n) ->
    if n < 10
      n = "0" + n
    n.toString()
  
  zp(d.getHours()) + ":" + zp(d.getMinutes()) + ":" + zp(d.getSeconds())

Handlebars.registerHelper 'epochdate', (epoch) ->
  d = new Date parseInt epoch * 1000
  
  zp = (n) ->
    if n < 10
      n = "0" + n
    n.toString()
  
  (d.getMonth() + 1) + "/" + zp(d.getDate()) + "/" + (1900 + d.getYear())
  
Handlebars.registerHelper 'featuresummary', (featureset) ->
  unless featureset?
    return
  #TODO, group by featuretype  
  ret = ''
  for f in featureset.models
    icon = ""
    if f.icon()
      icon = "<img src=\"" + f.icon() + "\">"
    ret += "<li class=feature>" + icon + f.represent() + "</li>"
    
  new Handlebars.SafeString(ret)
  
  
Handlebars.registerHelper 'featuredetail', (features) ->
  unless features[0].tableOk()?
    return new Handlebars.SafeString features[0].represent()
    
  ret = "<table class=\"tablesorter\"><thead><tr>"
  for th in features[0].tableHeader()
    ret += "<th>" + th + "</th>"
  ret += "</tr></thead><tbody>\n"

  for tr in features
     ret += "<tr>"
     for td in tr.tableData()
       ret += "<td>" + td + "</td>"
     ret += "</tr>"
  
  ret += "</tbody></table>"
  new Handlebars.SafeString(ret)
  
# Usage: {{#key_value obj}} Key: {{key}} // Value: {{value}} {{/key_value}}
Handlebars.registerHelper "key_value", (obj, fn) ->
  buffer = []
  retVal = []
  key = undefined
  for key of obj
    if obj.hasOwnProperty(key)
      buffer.push key
  _s = buffer.sort()
  for k in _s
    retVal += fn(
      key: k
      value: obj[k]
    )
  retVal
