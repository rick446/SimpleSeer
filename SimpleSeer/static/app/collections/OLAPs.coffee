Collection = require "./collection"
OLAP = require "models/OLAP"
ChartView = require 'views/chart'


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
