# Put your handlebars.js helpers here.
Handlebars.registerHelper 'epoch', (epoch) ->
  new Date parseInt epoch+'000'
