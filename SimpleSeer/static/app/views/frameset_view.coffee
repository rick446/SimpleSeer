View = require './view'

template = require './templates/frameset'
view_helper = require '../lib/view_helper'
application = require '../application'

module.exports = class FrameSet extends View
  template: template
  tagName: 'div'
  
  initialize: =>
    $('#frame-set-container').html @.$el
  
  events:
    #"mouseover .thumbnail": "hoverThumb"
    #"mouseout .thumbnail": "hoverThumb"
    "click .close-button": "closeThumb"
  
  hoverThumb: (target) =>
    if !$(target.relatedTarget).hasClass 'close-button'
      $(target.target).find('.close-button').toggleClass 'hidden'
    return
  
  closeThumb: (target) =>
    imageid = target.delegateTarget.id
    application.framesets._byId[@.id].removeFrame(target.currentTarget.id)
  
  getRenderData: =>
    @.options
    
  render: =>
    super()
    #console.log @.$el
    #$('#frame-set-container').html @.$el
    this
