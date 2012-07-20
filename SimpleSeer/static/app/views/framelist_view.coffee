View = require './view'
template = require './templates/framelist'
FramelistFrameView = require './framelistframe_view'
application = require '../application'
Frame = require "../../models/frame"
Filters = require "../../collections/filtercollection"

module.exports = class FramelistView extends View  
  template: template

  initialize: ()=>
    super()
    @empty=true
    @loading=false
    #@collection = collection
    @_frameViews = []
    @_newFrameViews = []
    @filter = {}
    @newFrames = []
    @total_frames = 0
    @showAll = false
    @rendered = false
    @lastLoadTime = new Date()
    @filtercollection = new Filters({model:Frame,view:@})
    $.datepicker.setDefaults $.datepicker.regional['']
    @page = "tabImage"

    #@collection.on 'add', @addFrame
    #@collection.on 'reset', @addFrames
    $(window).on 'scroll', @loadMore
    @filtercollection.on 'add', @addObj
    @filtercollection.on 'reset', @addObjs

    #application.socket.on "message:capture/", @capturedNewFrame
    #application.socket.emit 'subscribe', 'capture/'
    #setInterval @filterNew, 5000
    
  #events:
    #"submit #filter_form": "filterFrames"
    #"reset #filter_form": "filterFrames"
    #"click #load_new": "loadNew"
    #"click #filter_form input[name=time_to]": "setTimeToAsNow"

  events:
    'click #minimize-control-panel' : 'toggleMenu'
    'click .icon-item' : 'toggleMenu'
    'click #data-tab' : 'tabData'
    'click #image-tab' : 'tabImage'
  
  tabData: ()=>
    @page = "tabData"
    @filtercollection.limit = 65536
    @filtercollection.skip = 0
    @filtercollection.fetch
      success: () =>
        $('#image-view').hide()
        $('#data-view').show()
        $('#data-tab').removeClass('unselected')
        $('#image-tab').addClass('unselected')
        $('#data-views-controls').show()
        $('#views-controls').hide()
        $('#views-contain').addClass('wide scroll')
        $('#views').addClass('wide')
        $('#content').addClass('wide')

  tabImage: () =>
    @page = "tabImage"
    @filtercollection.limit = @filtercollection._defaults.limit
    @filtercollection.skip = @filtercollection._defaults.skip
    @filtercollection.fetch
      success: () =>
        $('#data-view').hide()
        $('#image-view').show()
        $('#image-tab').removeClass('unselected')
        $('#data-tab').addClass('unselected')
        $('#data-views-controls').hide()
        $('#views-controls').show()
        $('#views-contain').removeClass('wide')

  
  toggleMenu: ()=>
    if application.settings.showMenu
      application.settings.showMenu = false
      $('#second-tier-menu').hide()
      $("#stage").css('margin-left','0')
    else
      application.settings.showMenu = true
      $('#second-tier-menu').show()
      $("#stage").css('margin-left','252px')
  
  getRenderData: =>
    count_viewing: @filtercollection.length
    count_total: @filtercollection.totalavail
    count_new: @newFrames.length
    sortComboVals: @updateFilterCombo(false)

  render: =>
    @filtercollection.limit = @filtercollection._defaults.limit
    @filtercollection.skip = @filtercollection._defaults.skip
    if @rendered
      @.delegateEvents(@.events)
    @rendered = true
    super()
    #if @empty==true and @filtercollection.at(0)
    #  @newest = @filtercollection.at(0).get('capturetime')
    _(@_frameViews).each (fv) =>
      @$el.find('#frame_holder').append(fv.render().el)
    @$el.find('#loading_message').hide()
    @empty=false
    @lastLoadTime = new Date()
    return this
    
  afterRender: =>
    if !application.settings.showMenu?
      application.settings.showMenu = true
      @$el.find("#stage").css('margin-left','252px')
    @filtercollection.fetch()
    @$el.find('#sortCombo').combobox
      selected: (event, ui) =>
        if ui.item
          v = ui.item.value
        v = v.split(',')
        @filtercollection.sortList(v[0],v[1],v[2])
        #set sort order and key
      width:"50px"
    @$el.find("#tabDataTable").tablesorter()

  """
  postRender: =>
    camera_list = $('#filter_form select')
    for camera in application.settings.cameras
      camera_list.append '<option value="'+camera.name+'">'+camera.name+'</option>'
  """
  loadMore: (evt)=>
    if ($(window).scrollTop() >= $(document).height() - $(window).height()-1) && !@loading
      if (@filtercollection.length+1) <= @filtercollection.totalavail
    #if !@loading && $('#loading_message').length && @total_frames > 2\
    #   && (@total_frames - @filtercollection.length) > 0 && ($(window).scrollTop() >= $(document).height() - $(window).height())
        $('body').on('mousewheel', @disableEvent)
        enable = =>
          $('body').off('mousewheel', @disableEvent)
        setTimeout enable, 1000
        @$el.find('#loading_message').fadeIn('fast')
        @loading=true
        @filtercollection.skip += @filtercollection._defaults.limit
        @filtercollection.fetch()

  clearLoading: (callback=->)=>
    @loading = false
    @$el.find('#loading_message').fadeOut 1000, callback

  loadNew: ()=>
  """
    newFrameViews = _.clone(@_newFrameViews).sort (a,b)->
      if a.frame.get('capturetime') < b.frame.get('capturetime')
        return -1
      else
        return 1
    @_newFrameViews = []
    for fv in newFrameViews
      @$el.find('#frame_holder').prepend(fv.render().el)
    @$el.find('#count_viewing').html @filtercollection.length
    @$el.find('#count_new').html '0'
    @_frameViews = newFrameViews.concat(@_frameViews)
    @lastLoadTime = new Date()
  """
  filterNew: ()=>
    return
    if @newFrames.length
      filter = _.clone(@filter)
      # get the stuff that's been added between now and last load
      filter.time_to = (new Date).getTime()
      filter.time_from = @newest*1000
      @newFrames = []
      #@collection.fetch_filtered
      #  page: 0
      #  add: true
      #  filter: filter
      
  updateFilterCombo: (apply=true)=>
    out = []
    for o in @filtercollection.filters
      out.push({'label':o.options.params.label,'name':o.options.params.field_name,'type':o.options.params.type})
    return out
      

  addObj: (d)=>
    an = @$el.find('#frame_holder')
    @$el.find('#count_viewing').html @filtercollection.length
    @$el.find('#count_total').html @filtercollection.totalavail
    fv = new FramelistFrameView {model:d}
    if @page == "tabImage"
      an.append(fv.render().el)
    #else if @page == "tabData"
    #  @$el.find("#tabDataTable").tablesorter
    @clearLoading()

  addObjs: (d)=>
    an = @$el.find('#frame_holder')
    if @filtercollection.skip == 0
      an.html ''
    @$el.find('#count_viewing').html @filtercollection.length
    @$el.find('#count_total').html @filtercollection.totalavail    
    if @page == "tabImage"
      for o in d.models
        fv = new FramelistFrameView {model:o}
        an.append(fv.render().el)
    else if @page == "tabData"
      _empty = "---"
      @$el.find("#tabDataTable").find('tbody').html('')
      for o in d.models
        if o.attributes.features.models
          f = o.attributes.features.models[0].attributes.featuredata
        else
          f = {}
        dt = new moment(o.attributes.capturetime*1000)
        row = "<tr><td>"+dt.format("M-D-YY")+"</td><td>"+(f.head_width_mm||_empty)+"</td><td>"+(f.lbs_width_mm||_empty)+"</td><td>"+(f.shaft_width_mm||_empty)+"</td><td>"+(f.fillet_left_r||_empty)+"</td><td>"+(f.fillet_right_r||_empty)+"</td></tr>"
        row = $(row)
        resort = true; 
        @$el.find("#tabDataTable").find('tbody')
          .append(row) 
          .trigger('addRows', [row, resort]); 
      @$el.find("#tabDataTable").trigger('update')
    @clearLoading()

  """
  addFrame: (frame)=>
    #fv = new FramelistFrameView frame
    #@$el.find('#frame_holder').append(fv.render().el)
    #return
    @loading=false
    fv = new FramelistFrameView frame
    if frame.get('capturetime') > @newest
      @_newFrameViews.push fv
      @$el.find('#count_new').html @_newFrameViews.length
      @$el.find('#count_total').html @total_frames + @_newFrameViews.length
    else
      @_frameViews.push fv
      @total_frames = @filtercollection.total_frames
      if @$el.html() != ''
        next_page_size = @total_frames - @filtercollection.length

        @$el.find('#frame_holder').append(fv.render().el)
        @$el.find('#loading_message').fadeOut 1000, =>
          if next_page_size < 20
            @$el.find('#next_page_size').html next_page_size
        @$el.find('#count_viewing').html @_frameViews.length

  addFrames: (frames)=>
    @total_frames = 0
    if frames.length
      @$el.find('#frame_holder').html ''
      @$el.find('#frame_counts').show()
      frames.each @addFrame
    else
      @$el.find('#frame_holder').html '<p>No results found for this search.</p>'
  """
  """
  filterFrames: (evt)=>
    return
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
  """
  """
  fetchFiltered: =>
    skip = 0
    filter = _.clone(@filter)
    if !@empty
      skip = @_frameViews.length
      filter.time_to = @newest*1000
    @collection.fetch_filtered
      skip: skip
      filter: filter
  """
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
