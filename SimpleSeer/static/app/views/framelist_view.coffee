View = require './view'
template = require './templates/framelist'
FramelistFrameView = require './framelistframe_view'
application = require '../application'
Frame = require "../../models/frame"
Filters = require "../../collections/filtercollection"
tableView = require './widgets/tableView'

module.exports = class FramelistView extends View  
  template: template
  sideBarOpen: application.settings.showMenu
  lastModel: ""
  
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
    
    @tableView = @addSubview 'tabDataTable', tableView, '#tabDataTable',
      emptyCell:'---'
      columnOrder:["Capture Time","Left Fillet Angle&deg;","Right Fillet Angle&deg;","Part Number","Lot Number","Machine Number","First / Last Piece","Operator"]

    $(window).on 'scroll', @loadMore
    @filtercollection.on 'add', @addObj
    @filtercollection.on 'reset', @addObjs

  events:
    'click #minimize-control-panel' : 'toggleMenu'
    'click #second-tier-menu .title' : 'toggleMenu'
    'click .icon-item' : 'toggleMenu'
    'click #data-tab' : 'tabData'
    'click #image-tab' : 'tabImage'
    'click #viewStage .close' : 'closeViewStage'
  
  preFetch:()=>
    $('#loadThrob').modal "show"
  
  postFetch:()=>
    $('#loadThrob').modal "hide"
    url = @filtercollection.getUrl(true)
    $('#csvlink').attr('href','/downloadFrames/csv'+url)
    $('#excellink').attr('href','/downloadFrames/excel'+url)  
  
  tabData: ()=>
    $('#data-view').show()
    $('#data-tab').removeClass('unselected')
    $('#image-view').hide()
    $('#image-tab').addClass('unselected')
    $('#views-controls').hide()
    
    @page = "tabData"
    @filtercollection.limit = 65536
    @filtercollection.skip = 0
    @filtercollection.fetch
      before: @preFetch
      success: () =>
        $('#data-views-controls').show()
        $('#views-contain').addClass('wide scroll')
        $('#views').addClass('wide')
        $('#content').addClass('wide')
        @postFetch()

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
      before: @preFetch
      success: () =>
        $('#loadThrob').modal("hide");
        $('#data-views-controls').hide()
        $('#views-controls').show()
        $('#views-contain').removeClass('wide')
        @postFetch()

  toggleMenu: (callback) =>
    if !callback then callback = =>
    
    if application.settings.showMenu
      application.settings.showMenu = false
      $('#second-tier-menu').hide("slide", { direction: "left" }, 100)
      $("#stage").animate({'margin-left':'90px'}, 100, 'linear', callback)
    else
      @hideImageExpanded()
      application.settings.showMenu = true
      $('#second-tier-menu').show("slide", { direction: "left" }, 100)
      $("#stage").animate({'margin-left':'343px'}, 100, 'linear', callback)
  
  getRenderData: =>
    count_viewing: @filtercollection.length
    count_total: @filtercollection.totalavail
    count_new: @newFrames.length
    sortComboVals: @updateFilterCombo(false)
    metakeys: application.settings.ui_metadata_keys
    featurekeys: application.settings.ui_feature_keys
    filter_url:@filtercollection.getUrl()

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
      @$el.find("#stage").css('margin-left','343px')
    @filtercollection.fetch({before: @preFetch,success:@postFetch})
    @$el.find('#sortCombo').combobox
      selected: (event, ui) =>
        if ui.item
          v = ui.item.value
        v = v.split(',')
        @filtercollection.sortList(v[0],v[1],v[2])
        @filtercollection.fetch({before: @preFetch,success:@postFetch})
      width:"50px"
      
    application.settings.showMenu = true
      
    $(window).scroll =>
      @viewIsScrolled()

    $(window).resize =>
      if @lastModel and $(".currentExpanded").length > 0 
        @resizeExpanded()

  viewIsScrolled: =>
    if $(window).scrollTop() < 128 
      $("#viewStage").removeClass("fixit");
    else
      $("#viewStage").addClass("fixit");  
    
  closeViewStage: =>
    @hideImageExpanded()
    if @sideBarOpen then @toggleMenu()

  resizeExpanded: =>
    thumbnail = $($(".thumb").get 0)
    offsetLeft = thumbnail.offset().left + thumbnail.width() + 37
    imgWidth = thumbnail.parents("#views").width() - offsetLeft + 61
    $("#viewStage").css({"left": offsetLeft + "px", "width": imgWidth + "px", "display": "block"}).removeClass("fixit");
    
    framewidth = @lastModel.get("width")
    realwidth = imgWidth
    scale = realwidth / framewidth

    @pjs.size $('#viewStage').width(), @lastModel.get("height") * scale
    @pjs.scale scale
    
    $("#displaycanvas").height(@lastModel.get("height") * scale)
    if @lastModel.get('features') then @lastModel.get('features').each (f) => f.render(@pjs)
    @viewIsScrolled()    

  openUpExpanded: (element, frame, model) =>
    element.find(".image-view-item").addClass("currentExpanded");
    
    thumbnail = element.find(".thumb")
    offsetLeft = thumbnail.offset().left + thumbnail.width() + 37
    imgWidth = thumbnail.parents("#views").width() - offsetLeft + 61
    
    $("#displayimage").attr("src", frame.get('imgfile'));
    $("#viewStage").css({"left": offsetLeft + "px", "width": imgWidth + "px", "display": "block"}).removeClass("fixit");

    framewidth = model.get("width")
    realwidth = imgWidth
    scale = realwidth / framewidth   

    @pjs = new Processing($("#displaycanvas").get 0)
    @pjs.background(0,0)
    @pjs.size $('#viewStage').width(), model.get("height") * scale
    @pjs.scale scale
    
    $("#displaycanvas").height(model.get("height") * scale)
    if model.get('features') then model.get('features').each (f) => f.render(@pjs)
    @viewIsScrolled()
    @lastModel = model
    
  showImageExpanded: (element, frame, model) =>
    #console.log $(".currentExpanded")[0]
    #console.log element, frame, model
    $(".currentExpanded").removeClass("currentExpanded")
     
    if application.settings.showMenu
      @sideBarOpen = true
      @toggleMenu =>
        @openUpExpanded element, frame, model
    else
      @sideBarOpen = false
      @openUpExpanded element, frame, model

  hideImageExpanded: =>
    $("#viewStage").hide()
    $(".currentExpanded").removeClass("currentExpanded")

  loadMore: (evt)=>
    if ($(window).scrollTop() >= $(document).height() - $(window).height()-1) && !@loading && $("#views-controls :visible").length
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
        @filtercollection.fetch({before: @preFetch,success:@postFetch})

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
      @tableView.empty()
      for o in d.models
        fv = new FramelistFrameView {model:o}
        #fv.renderTableRow()
        fv.renderTableRow(@tableView)
        #@$el.find("#tabDataTable").find('tbody')
        #  .append(row) 
        #  .trigger('addRows', [row, resort]); 
      #@$el.find("#tabDataTable").trigger('update')
      @tableView.render()
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
