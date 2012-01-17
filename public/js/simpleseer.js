
/* Make sure the display is always relevant to the browser size
 * parts cribbed from http://jsfiddle.net/gaby/3YLQf/ */

SS = SimpleSeer = new Object();



//math helper functions
SimpleSeer.euclidean = function(pt1, pt2) {
    return Math.sqrt(Math.pow(pt1[0] - pt2[0], 2) + Math.pow(pt1[1] - pt2[1], 2));
}

SimpleSeer.clamp = function(val, min, max) {
    return Math.max(min, Math.min(max, val))
}








//function to retrieve data from webdis
SimpleSeer.getValue = function(key) {
    returndata = $.ajax({ url: "/GET/" + key + ".txt", 
                async: false, 
                dataType: 'json'
            }).responseText
    return returndata;
};

SimpleSeer.getJSON = function(key) {
    return $.parseJSON(SS.getValue(key));  
};



//functions to deal with adding/previewing/updating/deleting models
SimpleSeer.Inspection = {}

SimpleSeer.Inspection.add = function(method, parameters) {
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
    //TODO actually look up which display we're on
    
    $.post("/inspection_add", { name: name, camera: camera, method: method, parameters: JSON.stringify(parameters)}, 
        function(data) { 
            SS.inspections = data; });
};

SimpleSeer.Inspection.preview = function (method, parameters) {
    camera = SS.framedata[0]['camera'];
    
    data = SS.preview_data[camera];
    
    if (data) {
        SS.inspectionhandlers[method].render_features(data.features, data.inspection);
    }
    
    if (SS.previews_running[camera]) {
        return; //if there's already a preview running on this screen, wait
    }
    
    SS.previews_running[camera] = true;
    $.post("/inspection_preview", { name: "preview", camera: camera, method: method, parameters: JSON.stringify(parameters)},
        function(data) {   
            SS.preview_data[camera] = data;
            SS.previews_running[camera] = false;
            });
}

SimpleSeer.Inspection.render = function() {
    for (i in SS.inspections) {
        insp = SS.inspections[i]
        if (insp["method"] in SS.inspectionhandlers) {
            SS.inspectionhandlers[insp["method"]].render(insp) 
        }
    }
};

SimpleSeer.Inspection.remove = function(insp) {
    if (insp["method"] in SS.inspectionhandlers && "remove" in SS.inspectionhandlers[insp["method"]]) {
        SS.inspectionhandlers[insp["method"]].remove(insp);
    } 
    
    SS.action.task = "inspection_remove";
    
    $.post("/inspection_remove", { id: insp.id }, function(data) {
        SS.inspections = data;
        SS.resetAction();           
    });
};



SimpleSeer.Feature = {};
SimpleSeer.Feature.render = function() {
    //for (i in 
    
    
}

SimpleSeer.Measurement = {};
SimpleSeer.Measurement.render = function() {
    
}





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
  SS.resetAction();
}

SS.setScale = function() {
  SS.p.scale(SS.xscalefactor, SS.yscalefactor)
  SS.mouseX = Math.round(SS.p.mouseX / SS.xscalefactor);
  SS.mouseY = Math.round(SS.p.mouseY / SS.yscalefactor);
}

//these get registered to with each handler
SS.inspectionhandlers = {
    
    default: {

    },
    
    
    
    
    region: {
        render: function(insp) {
            SS.p.fill(255, 255, 255, 20);
            p = insp.parameters;
            SS.p.rect(p.x, p.y, p.w, p.h);
            
            id = insp.id;
            
            if (!$("#inspection_" + id).length){
                css_attr  = {
                    top: Math.round(p.y * SS.xscalefactor).toString() + "px",
                    left: Math.round(p.x * SS.yscalefactor),
                    width: Math.round(p.w * SS.xscalefactor),
                    height: Math.round(p.h * SS.yscalefactor)
                };

                $("<div/>", {
                    id: "inspection_" + id,
                    class: "stretchee object"
                }).appendTo('#maindisplay').css(css_attr).append(
                    $("<nav>", {
                        id: "manage_" + id,
                        class: "hidden", 
                    }).append('<a href="" title="Zoom"><b class="ico zoom-in"></b></a>'
                    ).append('<a href="" title="Zoom"><b class="ico zoom-out"></b></a>'
                    ).append('<a href="" title="Info"><b class="ico info"></b></a>'
                    ).append('<a class="inspection_remove" href="" title="Close"><b class="ico close"></b></a>'));
            
        
                $("#inspection_" + id).hover(function(){    /* shows the object nav bar */
                    $(this).css({ "z-index": 99 });
                    $(this).find('.hidden').removeClass('hidden');
                }, function(){
                    $(this).css({ "z-index": 80 });
                    $(this).find('nav').addClass('hidden');
                });
                
                $(".inspection_remove").click(function() {
                    SS.Inspection.remove(insp);
                    
                    return false;
                });
            }
        },
        
        remove: function(insp) {
            $("#inspection_" + insp.id).remove();
            SS.waitForClick();
        },
        render_features: function(feats, insp) {
            SS.p.fill(255, 20);
            
            
            
            
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
            
            SS.Inspection.add("region", {x: startx, y: starty, w: w, h: h});
            SS.resetAction();
            SS.waitForClick();
        }
    },
    blob: {
            
        render: function () {
            
            
        },
        render_features: function (features, inspection) {
            if (features.length == 0) {
                return;
            }
            SS.p.fill(0, 128, 0 , 80);
            for (i in features) {
                f = features[i];
                SS.p.beginShape();
                for (c in f.featuredata.mContour) {
                    pt = f.featuredata.mContour[c];
                    SS.p.vertex(pt[0], pt[1]);
                }
                SS.p.endShape();
            }
        },
        manipulate: function() {
            startx = SS.action['startpx'][0];
            starty = SS.action['startpx'][1];
            
            xdiff = startx - SS.mouseX;
            ydiff = starty - SS.mouseY;
            
            diff = xdiff * SS.xscalefactor;
            
            thresh = SS.clamp(128 + diff, 1, 254);
            
            SS.Inspection.preview("blob", { threshval: thresh, minsize: 1000 });            
        },
        manipulate_onclick: function() {
            //clean out the preview mode
            camera = SS.framedata[0]['camera'];
            insp = SS.preview_data[camera].inspection;
            SS.preview_data[camera] = false;
            
            SS.Inspection.add("blob", insp.parameters);
            SS.resetAction();
            SS.waitForClick();
        }
    }
}

//interface helpers, functions to control aspects of interface state
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


//the draw function is the loop() it can be enabled and disabled with SS.p.noLoop()
SS.p.draw = function() {
  SS.setScale();
  SS.p.background(0, 0);     
   
    
  if (SS.action["task"] && SS.action["task"] != "radial_select") {
      task = SS.action["task"];
      
      if (task in SS.inspectionhandlers) {
          if (SS.mouseDown) {
              SS.inspectionhandlers[task].manipulate_onclick();
          } else {
              SS.inspectionhandlers[task].manipulate();
          } 
          //or manipulate onclick
      }
  } else {
      SS.Inspection.render();  
      if (SS.mouseDown && !SS.mouseWait) {
          if (SS.wasPressed) {
            SS.launchRadial();
          } else {
            SS.launchRadial(true);   
          }
      } 
  }
  SS.wasPressed = SS.mouseDown;
 
 }


//TODO PUT ALL THESE in a "STATEMACHINE" object that gets backed up to redis
//import some context from webdis, 
SimpleSeer.cameras = SimpleSeer.getJSON('cameras');
SimpleSeer.previews_running = {};
SimpleSeer.preview_data = {}
for (c in SS.cameras) {
    SimpleSeer.previews_running[c] = false;
    SimpleSeer.previews_running[c] = false;
}

SimpleSeer.framecount = SimpleSeer.getValue('framecount');
SimpleSeer.framedata = [SimpleSeer.getJSON('currentframedata_0')];
SimpleSeer.poll_interval = parseFloat(SimpleSeer.getValue('poll_interval'));
SimpleSeer.inspections = SimpleSeer.getJSON('inspections');
SimpleSeer.histogram = SimpleSeer.getJSON('histogram_0');
SimpleSeer.radialAnimating = false;



SS.wasPressed = false;


SimpleSeer.waitForClick = function() {
    if (SS.mouseDown) {
        SS.mouseWait = true;
    }
}

SimpleSeer.resetAction = function() {
    SS.action = { startpx: [0,0], task: "" };
}



//initalize the display and the resize function
//TODO add any other independent behaviors
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
        $('.stretchee').remove();
    })

    $(window).load(function () {
        $(this).trigger('resize');
    });

});

//Setup executes when the display is ready to be initialized
SimpleSeer.setup = function(){
    SS.p.setup();
    SS.p.loop();

/* these functions just give us a little extra context for when processing doesn't pick up events*/
   $("#maindisplay").mousedown( function(e) {
      SS.mouseDown = true;
   });

   $("#maindisplay").mouseup( function(e) {
      SS.mouseDown = false;
      SS.mouseWait = false; 
   });

   $("#maindisplay").mousemove(function(e) {
  //SS.setScale();
    SS.p.mouseX = e.pageX - $("#display").offset()["left"];
    SS.p.mouseY = e.pageY - $("#display").offset()["top"];
   });

    
   //initialize the radial menu
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

   $("nav").draggable( {
        start: function(event, ui) { SS.action.task = "dragnav"; SS.waitForClick(); }, 
        stop: function(event, ui) { SS.action.task = ""; }    
   });

}


/*
$(document).ready(function() {
    $('.info').bind('click', function() {
        $(this).parent().parent().parent().find('.detail').toggle();
        $(this).parent().parent().addClass('expand');
        return false;
    });
});

SS.message = 
*/





//histogram
SS.histgraph = new Processing("histogram");

SS.histgraph.setup = function() {
    h = SS.histgraph;
    h.size(150, 48);
    h.background(0,0);
    h.stroke(255);
}


SS.histgraph.draw = function() {
    h = SS.histgraph;

    h.yscalefactor =  h.height / Math.max.apply(Math, SS.histogram);
    h.xstep = h.width / SS.histogram.length;
    
    for (i in SS.histogram) {
        x = h.xstep * i + 1;
        y = SS.histogram[i] * h.yscalefactor;
        
        h.line(x, h.height, x, h.height - y);
    }
}
SS.histgraph.setup();
SS.histgraph.draw();
