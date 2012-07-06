View = require './view'
template = require './templates/framelist'
FramelistFrameView = require './framelistframe_view'
application = require '../application'

module.exports = class FramelistView extends View  
  template: template

  initialize: (collection)=>
    super()
    @empty=true
    @loading=false
    @collection = collection
    @_frameViews = []
    @_newFrameViews = []
    @filter = {}
    @newFrames = []
    @total_frames = 0
    @lastLoadTime = new Date()
    $.datepicker.setDefaults $.datepicker.regional['']

    @collection.on 'add', @addFrame
    @collection.on 'reset', @addFrames
    $(window).on 'scroll', @loadMore

    application.socket.on "message:capture/", @capturedNewFrame
    application.socket.emit 'subscribe', 'capture/'
    setInterval @filterNew, 5000

  events:
    "submit #filter_form": "filterFrames"
    "reset #filter_form": "filterFrames"
    "click #load_new": "loadNew"
    "click #filter_form input[name=time_to]": "setTimeToAsNow"

  getRenderData: =>
    count_viewing: @collection.length
    count_total: @total_frames
    count_new: @newFrames.length

  render: =>
    super()
    if @empty==true and @collection.at(0)
      @newest = @collection.at(0).get('capturetime')
    _(@_frameViews).each (fv) =>
      @$el.find('#frame_holder').append(fv.render().el)
    @$el.find('#loading_message').hide()
    @empty=false
    @lastLoadTime = new Date()
    return this

  postRender: =>
    time_from_field = $('#filter_form input[name=time_from]').datetimepicker {timeFormat: 'hh:mm:ss'}
    if @collection.earliest_date
      time_from_field.datepicker( "setDate",  new Date(@collection.earliest_date*1000))
    $('#filter_form input[name=time_to]').datetimepicker {timeFormat: 'hh:mm:ss'}
    camera_list = $('#filter_form select')
    for camera in application.settings.cameras
      camera_list.append '<option value="'+camera.name+'">'+camera.name+'</option>'

  loadMore: (evt)=>
    if !@loading && $('#loading_message').length && @total_frames > 20\
       && (@total_frames - @collection.length) > 0 && ($(window).scrollTop() >= $(document).height() - $(window).height())
      $('body').on('mousewheel', @disableEvent)
      enable = =>
        $('body').off('mousewheel', @disableEvent)
      setTimeout enable, 1000
      @$el.find('#loading_message').fadeIn('fast')
      @loading=true
      @empty=false
      @fetchFiltered()

  loadNew: ()=>
    newFrameViews = _.clone(@_newFrameViews).sort (a,b)->
      if a.frame.get('capturetime') < b.frame.get('capturetime')
        return -1
      else
        return 1
    @_newFrameViews = []
    for fv in newFrameViews
      @$el.find('#frame_holder').prepend(fv.render().el)
    @$el.find('#count_viewing').html @collection.length
    @$el.find('#count_new').html '0'
    @_frameViews = newFrameViews.concat(@_frameViews)
    @lastLoadTime = new Date()

  filterNew: ()=>
    if @newFrames.length
      filter = _.clone(@filter)
      # get the stuff that's been added between now and last load
      filter.time_to = (new Date).getTime()
      filter.time_from = @newest*1000
      @newFrames = []
      @collection.fetch_filtered
        page: 0
        add: true
        filter: filter

  addFrame: (frame)=>
    @loading=false
    fv = new FramelistFrameView frame
    if frame.get('capturetime') > @newest
      @_newFrameViews.push fv
      @$el.find('#count_new').html @_newFrameViews.length
      @$el.find('#count_total').html @total_frames + @_newFrameViews.length
    else
      @_frameViews.push fv
      @total_frames = @collection.total_frames
      if @$el.html() != ''
        next_page_size = @total_frames - @collection.length

        @$el.find('#frame_holder').append(fv.render().el)
        @$el.find('#loading_message').fadeOut 1000, =>
          if next_page_size < 20
            @$el.find('#next_page_size').html next_page_size
        @$el.find('#count_viewing').html @_frameViews.length

  addFrames: (frames)=>
    if frames.length
      @$el.find('#frame_holder').html ''
      @$el.find('#frame_counts').show()
      frames.each @addFrame
    else
      @$el.find('#frame_holder').html '<p>No results found for this search.</p>'

  filterFrames: (evt)=>
    @filter = {}
    @empty = true
    if evt.type == 'submit'
      evt.preventDefault()
      _($('#filter_form').serializeArray()).each (input)=>
        if input.value != ''
          if input.name == 'time_from' || input.name == 'time_to'
            @filter[input.name] = Math.floor($('input[name='+input.name+']').datepicker( "getDate" ).getTime())
            if input.name == 'time_to'
              @newest = @filter[input.name]
          else
            @filter[input.name] = input.value
    @reset()
    @$el.find('#frame_holder').html 'Loading...'
    @$el.find('#frame_counts').hide()
    @fetchFiltered()

  fetchFiltered: =>
    skip = 0
    filter = _.clone(@filter)
    if !@empty
      skip = @_frameViews.length
      filter.time_to = @newest*1000
    @collection.fetch_filtered
      skip: skip
      filter: filter

  disableEvent: (evt)=>
    evt.preventDefault()
    return false

  reset: ()=>
    @_frameViews = []
    @empty = true
    @newFrames = []

  capturedNewFrame: (m)=>
    _(m.data.frame_ids).each (frame_id)=>
      @newFrames.push(frame_id)

  setTimeToAsNow: (evt)=>
    target = $(evt.target)
    if !target.val()
      target.datepicker("setDate", @lastLoadTime)