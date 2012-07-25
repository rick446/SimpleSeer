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

    $(window).on 'scroll', @loadMore
    @filtercollection.on 'add', @addObj
    @filtercollection.on 'reset', @addObjs

  events:
    'click #minimize-control-panel' : 'toggleMenu'
    'click .icon-item' : 'toggleMenu'
    'click #data-tab' : 'tabData'
    'click #image-tab' : 'tabImage'
  
  tabData: ()=>
    $('#loadThrob').modal("show");
    $('#data-view').show()
    $('#data-tab').removeClass('unselected')
    $('#image-view').hide()
    $('#image-tab').addClass('unselected')
    $('#views-controls').hide()
    
    @page = "tabData"
    @filtercollection.limit = 65536
    @filtercollection.skip = 0
    @filtercollection.fetch
      success: () =>
        $('#loadThrob').modal("hide");
        $('#data-views-controls').show()
        $('#views-contain').addClass('wide scroll')
        $('#views').addClass('wide')
        $('#content').addClass('wide')

  tabImage: () =>
    $('#loadThrob').modal("show");
    $('#image-view').show()
    $('#image-tab').removeClass('unselected')
    $('#data-view').hide()
    $('#data-tab').addClass('unselected')    
            
    @page = "tabImage"
    @filtercollection.limit = @filtercollection._defaults.limit
    @filtercollection.skip = @filtercollection._defaults.skip
    @filtercollection.fetch
      success: () =>
        $('#loadThrob').modal("hide");
        $('#data-views-controls').hide()
        $('#views-controls').show()
        $('#views-contain').removeClass('wide')

  
  toggleMenu: ()=>
    if application.settings.showMenu
      application.settings.showMenu = false
      $('#second-tier-menu').hide("slide", { direction: "left" }, 100)
      $("#stage").animate({'margin-left':'0px'}, 100)
    else
      application.settings.showMenu = true
      $('#second-tier-menu').show("slide", { direction: "left" }, 100)
      $("#stage").animate({'margin-left':'252px'}, 100)
  
  getRenderData: =>
    count_viewing: @filtercollection.length
    count_total: @filtercollection.totalavail
    count_new: @newFrames.length
    sortComboVals: @updateFilterCombo(false)
    metakeys: application.settings.ui_metadata_keys

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

  filterNew: ()=>
    return
    if @newFrames.length
      filter = _.clone(@filter)
      # get the stuff that's been added between now and last load
      filter.time_to = (new Date).getTime()
      filter.time_from = @newest*1000
      @newFrames = []
      
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
      resort = true
      @$el.find("#tabDataTable").find('tbody').html('')
      for o in d.models
        fv = new FramelistFrameView {model:o}
        fv.renderTableRow()
        row = fv.renderTableRow()
        @$el.find("#tabDataTable").find('tbody')
          .append(row) 
          .trigger('addRows', [row, resort]); 
      @$el.find("#tabDataTable").trigger('update')
    @clearLoading()

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
