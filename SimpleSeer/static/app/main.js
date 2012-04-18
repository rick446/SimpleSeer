require([
  "namespace",
  // Libs
  "jquery",
  "use!backbone",
  "use!simpleseer",
  "use!jquery_ui",
  "use!jqueryhoverIntent",
  
  //Modules
  "modules/inspection"
],

function(namespace, $, Backbone, SimpleSeer) {

  Inspection = require("modules/inspection");
  
  
  // Defining the application router, you can attach sub routers here.
  var Router = Backbone.Router.extend({
    
    initialize: function() {
      this.inspection = new Inspection.Router();
    },
    
    //Global routes
    routes: {
      "continuous": "continuous",
      "nextframe": "nextframe",
      "": "index",
      "watchlist": "watchlist",
      "hidewatchlist": "hidewatchlist",
      "zoomout": "zoomout"
      //":hash": "index"      
    },
    
    nextframe: function() {
      Backbone.history.navigate("", false);
      SimpleSeer.Frame.capture();  
    },

    index: function(hash) {
      var route = this;

      SimpleSeer.stopContinuous();
    },
    
    watchlist: function() {
        $("#watchlist_control").attr("href", "#hidewatchlist").toggleClass("watch").toggleClass("watched");
        SS.Watchlist.showWatchedItems();
    },
    
    hidewatchlist: function() {
        $("#watchlist_control").attr("href", "#watchlist").toggleClass("watch").toggleClass("watched");
        SS.Watchlist.hideWatchedItems();
    },
    
    continuous: function() {
        SimpleSeer.startContinuous();
    },
    
    zoomout: function() {
        //TODO, reset the href to inspection/zoomin/:id
        $(".zoom-out").toggleClass("zoom-in").toggleClass("zoom-out");
        SimpleSeer.zoomer.out();
    }
  });

  // Shorthand the application namespace
  var app = namespace.app;

  // Treat the jQuery ready function as the entry point to the application.
  // Inside this function, kick-off all initialization, everything up to this
  // point should be definitions.
  $(".tour").hide();
  SimpleSeer.setup();  //legacy setup NJO

    

  $(function() {
    // Define your master router on the application namespace and trigger all
    // navigation from this instance.
    app.router = new Router();
    


    // Trigger the initial route and enable HTML5 History API support
    Backbone.history.start({ pushState: true });
  });

  // All navigation that is relative should be passed through the navigate
  // method, to be processed by the router.  If the link has a data-bypass
  // attribute, bypass the delegation completely.
  $(document).on("click", "a:not([data-bypass])", function(evt) {
    // Get the anchor href and protcol
    var href = $(this).attr("href");
    var protocol = this.protocol + "//";

    // Ensure the protocol is not part of URL, meaning its relative.
    if (href && href.slice(0, protocol.length) !== protocol &&
        href.indexOf("javascript:") !== 0) {
      // Stop the default event to ensure the link will not cause a page
      // refresh.
      evt.preventDefault();

      // This uses the default router defined above, and not any routers
      // that may be placed in modules.  To have this work globally (at the
      // cost of losing all route events) you can change the following line
      // to: Backbone.history.navigate(href, true);
      app.router.navigate(href, true);
    }
  });
  
  //Autoresizing behaviors NJO
  var stretcher = $('#maindisplay').find('img'),
    element = stretcher[0],
    currentSize = { width: 0, height: 0 },
    $document = $(document);

  $(window).resize(function () {
    if (!SS.framedata) {
        return;
    }
    
    stretcher.width(1).height('auto');
    var w = $document.width();
    var h = $document.height();

    if (currentSize.width != w || currentSize.height != h) {
        stretcher.width(w).height('auto');
        if (h < element.height) {
            stretcher.width('auto').height(h);
        }
        currentSize.width = element.width;
        currentSize.height = element.height;
        
    }
    $('#display').height = stretcher.height();
    $('#display').width = stretcher.width();
    SS.p.size(stretcher.width(), stretcher.height());
    SS.xscalefactor = stretcher.width() /  SS.framedata[0].width
    SS.yscalefactor = stretcher.height() / SS.framedata[0].height
    $('.stretchee').remove();
    SS.p.refresh();
  });
  
  $(window).load(function () {
    $(this).trigger('resize');
  });

});
