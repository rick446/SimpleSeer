# Put your handlebars.js helpers here.
Handlebars.registerHelper 'epoch', (epoch) ->
  d = new Date parseInt epoch * 1000
  
  zp = (n) ->
    if n < 10
      n = "0" + n
    n.toString()
  
  (d.getMonth() + 1) + "/" + zp(d.getDate()) + " " + zp(d.getHours()) + ":" + zp(d.getMinutes()) + ":" + zp(d.getSeconds())
