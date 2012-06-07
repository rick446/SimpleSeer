Model = require "./model"
FrameSetView = require '../views/frameset_view'
application = require '../application'

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
    application.charts.unclickPoint fId
    @.save()
  parse: (response)=>
    @view = new FrameSetView(response)
    @view.render()
    response

