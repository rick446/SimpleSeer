require 'lib/slide_replace'
application = require 'application'
Frame = require "../models/frame"
FrameDetailView = require 'views/framedetail_view'

module.exports = class Router extends Backbone.Router
  routes: application.settings['ui_routes'] || {}

  for route, name of application.settings['ui_navurls']
    $('.nav').append '<li class="'+name.toLowerCase()+'"><a href="#'+route+'">'+name+'</a></li>'
  if application.settings['ui_enablenotebook']
    $('.nav').append '<li class="notebook"><a href=\'javascript: window.open(window.location.protocol + "//" + window.location.hostname + ":5050");\'>Develop</a></li>'

  home: ->
    application.charts.fetch
      success: (d1, d2) ->
        if application.settings['ui_enablesubnav']? and not application.settings['ui_enablesubnav']
          $('.subnav').hide()
        $('ul.nav').find(".active").removeClass("active")
        $('ul.nav').find('li.charts').addClass('active')
        $('#main').slideReplace application.homeView.render().el, 'left'
        application.homeView.subviews.frameview.setVideoFeed()
        application.charts.onSuccess(d1, d2)
        application.homeView.postRender()
        
  framelist: ->
    application.framelistView.reset()
    application.lastframes.fetch_filtered
      success: ->
        $('ul.nav').find(".active").removeClass("active")
        $('ul.nav').find('li.frames').addClass('active')
        $('#main').slideReplace application.framelistView.render().el, 'right'
        application.framelistView.postRender()
        
        
  frame: (id) ->
    frame_view = (f) ->
      fdv = new FrameDetailView({model: f})
      $('#main').slideReplace fdv.render().el, 'right'
      fdv.postRender()
       
    f = application.lastframes.get(id)
    if f
      frame_view f
    else
      f = new Frame {id: id}
      f.fetch
        success: ->
          frame_view f
