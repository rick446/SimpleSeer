
/* Make sure the display is always relevant to the browser size
 * parts cribbed from http://jsfiddle.net/gaby/3YLQf/ */

SS = SimpleSeer = new Object();

//initalize the display and the resize function
$(function(){

    var stretcher = $('#maindisplay > img'),
        element = stretcher[0],
        currentSize = { width: 0, height: 0 },
        $document = $(document);

    $(window).resize(function () {
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
    })

    $(window).load(function () {
        $(this).trigger('resize');
    });

});

//function to retrieve data from webdis
SimpleSeer.getValue = function(key) {
    returndata = $.parseJSON(
        $.ajax({ url: "/GET/" + key + ".json", 
                async: false, 
                dataType: 'json'
            }).responseText
    );
    return returndata['GET'];
};

//import some context from webdis
SimpleSeer.cameras = SimpleSeer.getValue('cameras');
SimpleSeer.framecount = SimpleSeer.getValue('framecount');
SimpleSeer.framedata = [$.parseJSON(SimpleSeer.getValue('currentframedata_0'))];
SimpleSeer.poll_interval = parseFloat(SimpleSeer.getValue('poll_interval'));

/* //check the frame id, if it increments, reload context
setInterval(function(){
   thisframe = SimpleSeer.getValue('framecount');
   if (SimpleSeer.framecount != thisframe) {
       d = new Date();
       $('#maindisplay > img').attr("src", "/GET/currentframe_0.jpg?" + d.getTime());
   }
   SimpleSeer.framecount = thisframe;

}, SimpleSeer.poll_interval * 1000);
 */


SS.p = new Processing('display');
//coloquially, we'll probably always refer to this as SS.p

//this is the "main" loop of the processing app

SS.p.setup = function() {
  SS.p.size($('#maindisplay > img').width(), $('#maindisplay > img').height());
  SS.action = { startpx: [0,0], task: "" }
}

SS.setscale = function() {
  SS.p.scale(SS.xscalefactor, SS.yscalefactor)
  SS.mouseX = Math.round(SS.p.mouseX / SS.xscalefactor);
  SS.mouseY = Math.round(SS.p.mouseY / SS.yscalefactor);
}

//these get registered to with each handler
SS.taskhandler = {
    ROI: {
        render: function() {
            
            
            
            
            
            
        },
        callback: function() {
            
            
            
            
            
        },
        
        manipulate: function() {
            startx = SS.action['startpx'][0];
            starty = SS.action['startpx'][1];
            
            w = Math.abs(startx - SS.mouseX);
            h = Math.abs(starty - SS.mouseY);
            
            if (startx > SS.mouseX) {
                startx = SS.mouseX;
            }
            if (starty > SS.mouseY) {
                starty = SS.mouseY;
            }
            
            SS.p.fill(255, 20);
            SS.p.rect(startx, starty, w, h);
        }
        
        manipulate_onclick: function() {
            
            startx = SS.action['startpx'][0];
            starty = SS.action['startpx'][1];
            
            w = Math.abs(startx - SS.mouseX);
            h = Math.abs(starty - SS.mouseY);
            
            if (startx > SS.mouseX) {
                startx = SS.mouseX;
            }
            if (starty > SS.mouseY) {
                starty = SS.mouseY;
            }
            
            SS.addInspection("region", {x: startx, y: starty, w: w, h: h});
            
            
        }
    }
    
    
    
    
    
}

SS.p.draw = function() {
  SS.setscale();
  SS.p.background(0, 0);     
  
  
  if (SS.action["task"]) {
      task = SS.action["task"];
      
      if (task in SS.taskhandler) {
          SS.taskhandler[task].manipulate();
      }
      
      
      
  }
  
  //SS.p.fill(255, 20);  
  //SS.p.rect(SS.mouseX, SS.mouseY, 20, 20);  
 }

 
SS.p.mousePressed = function() {
  //SS.setscale();
  
    if (!SS.action["task"]) {
        SS.action = { startpx: [SS.mouseX, SS.mouseY], task: "radial_select" };
        $("#radial").radmenu("show").css( { zIndex: 99, top: SS.p.mouseY.toString() + "px", left: SS.p.mouseX.toString() + "px" } );
    } else {
        if (task in SS.taskhandler) {
            SS.taskhandler[task].manipulate_onclick();
        }
    }
}

//this executes at document.ready
SimpleSeer.setup = function(){
    SS.p.setup();
    SS.p.loop();
    
    $("#radial").radmenu({
        listClass: 'radial_items', // the list class to look within for items
        itemClass: 'radial_item', // the items - NOTE: the HTML inside the item is copied into the menu item
        radius: 100, // radius in pixels
        animSpeed:400, // animation speed in millis
        centerX: -10, // the center x axis offset
        centerY: -10, // the center y axis offset
        selectEvent: "click", // the select event (click)
        onSelect: function($selected){ // show what is returned 
            id = $selected.children()[0].id;
            task = id.substr(12); //get the task from the id
            SS.action["task"] = task;
        
            $("#radial").radmenu("hide").css( { zIndex: -1, top: "0px", left: "0px" } );

        },
        angleOffset: 0 // in degrees
    });
}
