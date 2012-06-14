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
    @filter = {}
    $.datepicker.setDefaults $.datepicker.regional['']

    @collection.on('add', @addFrame)
    @collection.on('reset', @addFrames)
    $(window).on('scroll', @loadMore)
  
  events:
    "submit #filter_form": "filterFrames"
    "reset #filter_form": "filterFrames"

  getRenderData: =>
    count_viewing: @collection.length
    count_total: @collection.total_frames

  render: =>
    super()
    if @pages==1
      @newest = @collection.at(0).get('capturetime')
    _(@_frameViews).each (fv) =>
      @$el.find('#frame_holder').append(fv.render().el)
    @$el.find('#loading_message').hide()
    return this

  postRender: =>
    $('#filter_form input[name=time_from]').datetimepicker {timeFormat: 'hh:mm:ss'}
    $('#filter_form input[name=time_to]').datetimepicker {timeFormat: 'hh:mm:ss'}

  loadMore: (evt)=>
    if !@loading && $('#loading_message').length && ($(window).scrollTop() >= $(document).height() - $(window).height())
      $('body').on('mousewheel', @disableEvent)
      enable = =>
        $('body').off('mousewheel', @disableEvent)
      setTimeout enable, 1000
      @$el.find('#loading_message').fadeIn('fast')
      @loading=true
      @pages=@pages+1
      @fetchFiltered()

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
    if frames.length
      @$el.find('#frame_holder').html ''
      @$el.find('#frame_counts').show()
      frames.each @addFrame
    else
      @$el.find('#frame_holder').html '<p>No results found for this search.</p>'

  filterFrames: (evt)=>
    @filter = {}
    @pages = 1
    if evt.type == 'submit'
      evt.preventDefault()
      _($('#filter_form').serializeArray()).each (input)=>
        if input.value != ''
          if input.name == 'time_from' || input.name == 'time_to'
            @filter[input.name] = Math.floor($('input[name='+input.name+']').datepicker( "getDate" ).getTime())
          else
            @filter[input.name] = input.value
    @$el.find('#frame_holder').html 'Loading...'
    @$el.find('#frame_counts').hide()
    @fetchFiltered()

  fetchFiltered: =>
    @collection.fetch_filtered
      page: @pages
      filter: @filter

  disableEvent: (evt)=>
    evt.preventDefault()
    return false
