Collection = require "./collection"
OLAP = require "models/OLAP"
ChartView = require 'views/chart'
application = require 'application'


module.exports = class OLAPs extends Collection
  url: "/api/olap"
  model: OLAP

  onSuccess: (d1, d2) =>
    for me in d2
      #d1.buildChart d1.get me.id
      mod = d1.get me.id
      if !mod.view
        mod.view = new ChartView()
        mod.view.anchorId = me.id
        mod.view.render()
    return
  pause: (fId) =>
    if !fId
      #todo: grab latest frame
      fId = ''
    fDom = $('#frame img')
    if !fDom.attr('live')
      fDom.attr('live',fDom.attr('src'))
    fDom.attr('src','/grid/imgfile/'+fId)
    for obj in @.models
      application.socket.emit 'unsubscribe', 'OLAP/'+obj.attributes.name+'/'
    application.alert('<a href="#">Paused</a>','error')
  unPause: =>
    for obj in @.models
      application.socket.emit 'subscribe', 'OLAP/'+obj.attributes.name+'/'
    $('.alert_error').remove();
    fDom = $('#frame img')
    fDom.attr('src',fDom.attr('live'))



