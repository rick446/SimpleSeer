Model = require "./model"

module.exports = class FrameSet extends Model
  urlRoot: -> "/api/frameset"

  addFrame: (fId)=>
    if fId not in @.attributes.frames
      @.attributes.frames.push(fId)
  removeFrame: (fId)=>
    @.attributes.frames = $.grep(@.attributes.frames, (k,i)->
      if k == fId
        return false
      return true
    )
