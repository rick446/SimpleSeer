Model = require "./model"
FrameSetView = require '../views/frameset_view'


module.exports = class FrameSet extends Model
  urlRoot: -> "/api/frameset"

  addFrame: (fId)=>
    if fId not in @.attributes.frames
      @.attributes.frames.push(fId)
      @.view.render()
      @.save()
  removeFrame: (fId)=>
    @.attributes.frames = $.grep(@.attributes.frames, (k,i)->
      if k == fId
        return false
      return true
    )
    @.save()
  parse: (response)=>
    @view = new FrameSetView(response)
    @view.render()
    response

