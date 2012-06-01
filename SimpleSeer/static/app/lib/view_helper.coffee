# Put your handlebars.js helpers here.
Handlebars.registerHelper 'epoch', (epoch) ->
  d = new Date parseInt epoch * 1000
  
  zp = (n) ->
    if n < 10
      n = "0" + n
    n.toString()
  
  (d.getMonth() + 1) + "/" + zp(d.getDate()) + " " + zp(d.getHours()) + ":" + zp(d.getMinutes()) + ":" + zp(d.getSeconds())
  
  
Handlebars.registerHelper 'featuresummary', (featureset) ->
  unless featureset?
    return
  #TODO, group by featuretype  
  ret = ''
  for f in featureset.models
    ret += "<li>" + f.represent() + "</li>"
    
  new Handlebars.SafeString(ret)
  
  
Handlebars.registerHelper 'featuredetail', (features) ->
  unless features[0].tableOk()?
    return new Handlebars.SafeString features[0].represent()
    
  ret = "<table><tr>"
  for th in features[0].tableHeader()
    ret += "<th>" + th + "</th>"
  ret += "</tr>\n"

  for tr in features
     ret += "<tr>"
     for td in tr.tableData()
       ret += "<td>" + td + "</td>"
     ret += "</tr>"
  
  ret += "</table>"
  new Handlebars.SafeString(ret)
