
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


SimpleSeer.resetAction = function() {
    SS.action = { startpx: [0,0], task: "" };
}


//function to retrieve data from webdis
SimpleSeer.getValue = function(key) {
    returndata = $.ajax({ url: "/GET/" + key + ".txt", 
                async: false, 
                dataType: 'json'
            })
    return returndata;
};

SimpleSeer.getJSON = function(key) {
    return $.parseJSON(SS.getValue(key));  
};


SimpleSeer.addInspection = function(method, parameters) {
    inspection_names = {};
    for (i in SS.inspections) {
        inspection_names[i.name] = 1;
    } //build a table of names
    
    counter = 1;
    name = method + counter.toString();
    while (name in inspection_names) {
        counter++;
        name = method + counter.toString();
    } //Find the lowest available number for a default name
    
    camera = SS.framedata[0]['camera'];
    
    $.post("/inspection_add", { name: name, camera: camera, method: method, parameters: JSON.stringify(parameters)}, 
        function(data) {  SS.renderInspections() });
    
};

SimpleSeer.renderInspections = function() {
    //alert("rendered!");
};


//math helper functions
SimpleSeer.euclidean = function(pt1, pt2) {
    return Math.sqrt(Math.pow(pt1[0] - pt2[0], 2) + Math.pow(pt1[1] - pt2[1], 2));
}


//import some context from webdis
SimpleSeer.cameras = SimpleSeer.getValue('cameras');
SimpleSeer.framecount = SimpleSeer.getValue('framecount');
SimpleSeer.framedata = [$.parseJSON(SimpleSeer.getValue('currentframedata_0'))];
SimpleSeer.poll_interval = parseFloat(SimpleSeer.getValue('poll_interval'));
//SimpleSeer.inspections = SimpleSeer.getValue('inspections');

SimpleSeer.radialAnimating = false;



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
  SS.resetAction()
}

SS.setscale = function() {
  SS.p.scale(SS.xscalefactor, SS.yscalefactor)
  SS.mouseX = Math.round(SS.p.mouseX / SS.xscalefactor);
  SS.mouseY = Math.round(SS.p.mouseY / SS.yscalefactor);
}

//these get registered to with each handler
SS.taskhandler = {
    roi: {
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
        },
        
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
            SS.resetAction();
            
        }
    }
}


SS.launchRadial = function(animate) {
    
    if (SS.radialAnimating) {
        return;
    }
    oldtask = SS.action["task"];
    
    if (oldtask == "radial_select") {
        distance = SS.xscalefactor * SS.euclidean(SS.action["startpx"], [SS.mouseX, SS.mouseY]);
        if (distance > 75 && animate) { 
            SS.radialAnimating = true;
            $("#radial_container").animate( {
                top: (SS.p.mouseY - 110).toString() + "px", 
                left: (SS.p.mouseX - 110).toString() + "px" }, 300,
                function() { SS.radialAnimating = false; } 
            );    
        } else {
            $("#radial_container").css( {
                top: (SS.p.mouseY - 110).toString() + "px", 
                left: (SS.p.mouseX - 110).toString() + "px" 
            });   
        }   
    } else {
        $("#radial_container").radmenu("show").css( { zIndex: 99,
            top: (SS.p.mouseY - 110).toString() + "px", 
            left: (SS.p.mouseX - 110).toString() + "px" } );
    }


    SS.action = { startpx: [SS.mouseX, SS.mouseY], task: "radial_select" };
    
}

SS.wasPressed = false;
SS.p.draw = function() {
  SS.setscale();
  SS.p.background(0, 0);     
    
  if (SS.action["task"] && SS.action["task"] != "radial_select") {
      task = SS.action["task"];
      
      if (task in SS.taskhandler) {
          if (SS.mouseDown) {
              SS.taskhandler[task].manipulate_onclick();
          } else {
              SS.taskhandler[task].manipulate();
          } 
          //or manipulate onclick
      }
  } else {
      
      if (SS.mouseDown) {
          if (SS.wasPressed) {
            SS.launchRadial();
          } else {
            SS.launchRadial(true);   
          }
      } 
  }
  SS.wasPressed = SS.mouseDown;
  //SS.p.fill(255, 20);  
  //SS.p.rect(SS.mouseX, SS.mouseY, 20, 20);  
 }



//this executes at document.ready
SimpleSeer.setup = function(){
    SS.p.setup();
    SS.p.loop();

/* these functions just give us a little extra context for when processing doesn't pick up events*/
   $("#maindisplay").mousedown( function(e) {
      SS.mouseDown = true;
   });

   $("#maindisplay").mouseup( function(e) {
      SS.mouseDown = false; 
   });

   $("#maindisplay").mousemove(function(e) {
  //SS.setscale();
    SS.p.mouseX = e.pageX - $("#display").offset()["left"];
    SS.p.mouseY = e.pageY - $("#display").offset()["top"];
   });
/*end processing helpers*/

    

   $("#radial_container").radmenu({
        listClass: 'radiallist', // the list class to look within for items
        itemClass: 'radialitem', // the items - NOTE: the HTML inside the item is copied into the menu item
        radius: 68, // radius in pixels
        centerX: 10, // the center x axis offset
        centerY: -6, // the center y axis offset
        selectEvent: "mousedown", // the select event (click)
        onSelect: function($selected){ // show what is returned 
          $('#radial_container').radmenu("hide");
          SS.action['task'] = $selected.children()[0].id.substr(7); //remove the #radial prefix
        },
        onShow: function($items){$items.show();$('#radial_container').fadeIn(500);},
        onHide: function($items){$items.hide();$('#radial_container').fadeOut(500);}
      });

}
