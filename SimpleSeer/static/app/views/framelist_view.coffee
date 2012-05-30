View = require './view'
template = require './templates/framelist'
FramelistFrameView = require './framelistframe_view'

module.exports = class FramelistView extends View  
  template: template

  initialize: (collection)=>
    super()
    @pages=1
    @loading=false
    @collection = collection
    @_frameViews = []

    @collection.on('add', @addFrame)
    @collection.on('reset', @addFrames)
    $(window).on('scroll', @loadMore)
  
  getRenderData: =>
    count_viewing: @collection.length

  render: =>
    super()
    if @pages==1
      @newest = @collection.at(0).get('capturetime')
    _(@_frameViews).each (fv) =>
      @$el.find('#frame_holder').append(fv.render().el)
    @$el.find('#loading_message').hide()
    return this

  loadMore: (evt)=>
    if !@loading && ($(window).scrollTop() >= $(document).height() - $(window).height())
      $('body').on('mousewheel', @disableEvent)
      enable = =>
        $('body').off('mousewheel', @disableEvent)
      setTimeout enable, 1000
      @$el.find('#loading_message').fadeIn('fast')
      @loading=true
      @pages=@pages+1
      @collection.fetch
        add: true
        data:
          page: @pages
          before: @newest

  addFrame: (frame)=>
    @loading=false
    fv = new FramelistFrameView frame
    @_frameViews.push fv
    if @$el.html() != ''
      next_page_size = @collection.total_frames - @collection.length

      if next_page_size <= 0
        $(window).off('scroll', @loadMore)
      @$el.find('#frame_holder').append(fv.render().el)
      @$el.find('#loading_message').fadeOut 1000, =>
        if next_page_size < 20
          @$el.find('#next_page_size').html next_page_size
      @$el.find('#count_viewing').html @collection.length

  addFrames: (frames)=>
    frames.each @addFrame

  disableEvent: (evt)=>
    evt.preventDefault()
    return false