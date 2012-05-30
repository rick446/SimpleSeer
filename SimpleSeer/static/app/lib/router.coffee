require 'lib/slide_replace'
application = require 'application'


module.exports = class Router extends Backbone.Router
  routes:
    '': 'home'
    'frames': 'framelist'

  home: ->
    application.charts.fetch
      success: (d1, d2) ->
        $('ul.nav').find(".active").removeClass("active")
        $('ul.nav').find('li.charts').addClass('active')
        $('#main').slideReplace application.homeView.render().el, 'left'
        application.homeView.subviews.frameview.setVideoFeed()
        application.charts.onSuccess(d1, d2)
        application.homeView.postRender()
        
  framelist: ->
    application.lastframes.fetch
      success: ->
        $('ul.nav').find(".active").removeClass("active")
        $('ul.nav').find('li.frames').addClass('active')
        $('#main').slideReplace application.framelistView.render().el, 'right'

