Model = require "./model"

module.exports = class OLAP extends Model
  urlRoot: -> "/api/olap"

  pointStack: () ->
    stack : []
    add: (d,shift=true) ->
      _a = {x:d.x.toString(),y:d.y,id:d.id.toString()}
      @.stack.push _a
      if shift
        p = @.stack.shift()
      return p
    set: (d) ->
      @stack = []
      for o in d
        @.add o, false
    buildData: (data) =>
      if !data
        data = @.view.chart.stack.stack
      dd = []
      if @.attributes.chartInfo.map
        for i of @.attributes.chartInfo.map
          dd[i] = {x:i,id:i,y:0}
          if @.attributes.chartInfo.colormap && @.attributes.chartInfo.colormap[i]
            dd[i].color = @.attributes.chartInfo.colormap[i]
      _stk = []
      for d in data
        if !d.x
          p = @.view._formatChartPoint d
        else p = d
        if dd[p.id]
          p = dd[p.id]
          p.y++
        else
          p.y = 1
        dd[p.id] = p
        _stk.push p
      _dd = []
      for i in dd
        if i
          _dd.push i
      @.view.chart.stack.set _stk
      return _dd
  


