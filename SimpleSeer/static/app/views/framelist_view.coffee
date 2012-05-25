View = require './view'
template = require './templates/framelist'
app = require "application"

module.exports = class FramelistView extends View  
  template: template

  initialize: (collection)=>
    super()
    @pages=1
    @loading=false
    @collection = collection
    console.info @collection

    $(window).scroll @loadMore #have to bind this event here instead of events because it's on window
  
  getRenderData: =>
    # if this is the first time we're rendering, set the collection up
    if @pages==1
      @newest = @collection.at(0).get('capturetime')
    @loading=false
    frames: @collection.map (frame) ->
      capturetime: new Date parseInt frame.get('capturetime')+'000'
      camera: frame.get('camera')
      imgfile: frame.get('imgfile')
      id: frame.get('id')

  loadMore: =>
    if !@loading && ($(window).scrollTop() > $(document).height() - $(window).height() - 300)
      @loading=true
      @pages=@pages+1
      @collection.fetch
        add: true
        data:
          page: @pages
          before: @newest
        success: @render #20 add events get fired off this and only needs to render once so don't bind