Model = require "./model"

module.exports = class OLAP extends Model
  urlRoot: -> "/api/chart"

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
        data = @.view.stack.stack
      dd = []
      console.log @.attributes.labelmap.length
      if @.attributes.labelmap && @.attributes.labelmap.length > 0
        for i of @.attributes.labelmap
          dd[i] = {x:i,id:i,y:0}
          if @.attributes.colormap && @.attributes.colormap[i]
            dd[i].color = @.attributes.colormap[i]
      _stk = []
      for d in data
        if !d.x
          p = @.view._formatChartPoint d
        else
          p = d
        if dd[p.id]
          p = dd[p.id]
          p.y++
        else
          p.y = 1
        dd[p.id] = p
        _stk.push p
      #if @.view.lib == 'custom'
      #  console.log dd
      _dd = []
      for i in dd
        if i
          _dd.push i
      @.view.stack.set _stk
      #if @.view.lib == 'custom'
      #  console.log @.view.stack.stack

      return _dd
