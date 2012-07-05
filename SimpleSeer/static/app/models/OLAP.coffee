Model = require "./model"

module.exports = class OLAP extends Model
  urlRoot: -> "/api/chart"

  pointStack: () ->
    stack : []
    add: (d,shift=false) ->
      #_a = {x:d.x,y:d.y,id:d.id}
      @.stack.push d
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
      if @.attributes.labelmap
        for i of @.attributes.labelmap
          dd[i] = {x:i,id:i,y:0}
          if @.attributes.colormap && @.attributes.colormap[i]
            dd[i].color = @.attributes.colormap[i]
      _stk = []
      for p in data
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
      @.view.stack.set _stk
      return _dd
