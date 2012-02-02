
isEmpty = function(obj) {
    for (var prop in obj) {
        if (obj.hasOwnProperty(prop)) return false;
    }
    return true;
};

//http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript
capitalize = function(){
   return this.replace( /(^|\s)([a-z])/g , function(m,p1,p2){ return p1+p2.toUpperCase(); } );
};


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



SimpleSeer.DisplayObject = {};


SimpleSeer.DisplayObject.addNavItem = function(id, iconcls, title, clickmethod) {
    //TODO, when nav is close to right side, flip to left-nav (css class)
    
    $("#" + id).find("nav").append(
       $("<a/>", { title: title, href: "#" }).append($("<b/>", { class: "ico " +iconcls })).click(clickmethod)
    );
}

SimpleSeer.DisplayObject.addNavZoomIn = function(id) {
    SS.DisplayObject.addNavItem(id, "zoom-in", "Zoom", function(e) {
        SS.zoomer.in( { element:$(e.target).parent().parent().parent()[0] } );
        SS.mouseBlock = false;
        return false;
    });
}

SimpleSeer.DisplayObject.addNavZoomOut = function(id) {
    SS.DisplayObject.addNavItem(id, "zoom-out", "Zoom Out", function(e) {
        SS.zoomer.out();
        SS.mouseBlock = false;
        return false;
    });
}

SimpleSeer.DisplayObject.addNavInfo = function(id, title, info, inspection, featureindex) {
    SS.DisplayObject.addNavItem(id, "info", "Info", function(e) {
        $(e.target).parent().parent().find(".detail").fadeIn(300);
        return false;
    });
    
    
    watchlist = $("<div/>", { class: "detail" }).append(title);
    for (prop in info) {
        value = SS.featuresets[inspection.id][featureindex][prop];
        label = info[prop].label;
        method = prop;
        
        units = ''
        if ("units" in info[prop]) {
            units = info[prop].units;
        } 
        
        if ("handler" in info[prop]) {
            value = info[prop].handler(value);
        }
        
        var watchclass = "ico watch";
        
        
        //TODO make the eye toggle properly onclick
        var watchfunction = function(i, fc, m) { return function() {
            SS.Measurement.add({ inspection: i,
                featurecriteria: fc,
                method: m
            });
            return false;
        } }(inspection, { index: featureindex}, method);
        
        meas = SS.Inspection.findMeasurement(inspection, { index: featureindex }, prop);
        if (meas) {
            watchclass = "ico watched"
            watchfunction = function(m) { return function() {
                SS.Measurement.remove(m);
                return false;
            }}(meas);
        }
        
        watchlist.append($("<p/>").append(label + ": " + value + units).append(
            $("<a/>", { href: "", title: "Watch" }).append(
                $("<b/>", { class: watchclass})
            ).click(watchfunction)
        ));
    }
    
    $("#" + id).find("nav").append(watchlist)
}

SimpleSeer.Display = {};


SimpleSeer.Display.renderObjectFocus = function(id) {
    
      if (SS.zoomer.zoomLevel() > 1) {
            return;
      } 
      focusdiv = $("#" + id);
      offset = focusdiv.offset();
      
      xy = SS.processingToImageCoordinates(offset.left, offset.top);
      wh = SS.processingToImageCoordinates(focusdiv.width(), focusdiv.height());
      
      x = xy[0];
      y = xy[1];
      w = wh[0];
      h = wh[1]; 

      var imgw = SS.framedata[0].width;
      var imgh = SS.framedata[0].height;
      
      
      SS.p.fill(0, 80);
      SS.p.noStroke();
      
      SS.p.beginShape();
      
      SS.p.vertex(0,0);
      SS.p.vertex(x, 0);
      SS.p.vertex(x, y + h);
      SS.p.vertex(imgw, y + h);
      SS.p.vertex(imgw, imgh);
      SS.p.vertex(0, imgh);
      SS.p.endShape(SS.p.CLOSE);
    
      SS.p.beginShape();
      SS.p.vertex(x, 0);
      SS.p.vertex(imgw, 0);
      SS.p.vertex(imgw, y + h);
      SS.p.vertex(x + w, y + h);
      SS.p.vertex(x + w, y);
      SS.p.vertex(x, y);
      SS.p.endShape(SS.p.CLOSE);
      
      SS.p.stroke(0);
      SS.p.noFill();
      SS.p.rect(x,y,w,h);
      
}


SimpleSeer.Display.addDisplayObject = function(id, x, y, w, h) {

    
    $("#" + id).remove(); //delete any existing object with this ID
    
    objdiv = $("<div/>", {
        id: id,
        class: "stretchee object"
    }).css({
        top: Math.round(y * SS.xscalefactor).toString() + "px",
        left: Math.round(x * SS.yscalefactor),
        width: Math.round(w * SS.xscalefactor),
        height: Math.round(h * SS.yscalefactor)
    }).appendTo('#zoomer').append(
        $("<nav>", {
            id: "manage_" + id,
            style: "display: none" 
        }).hover( function() {
                SS.mouseBlock = true;
            }, function() {
                SS.mouseBlock = false;
            })
        );
    
    $("#" + id).hoverIntent({
       over: function(){    /* shows the object nav bar */
        $(this).css({ "z-index": 99 });
        $(this).find('nav').fadeIn(200);
        SS.action["focus"] = id;
    }, out: function(){
        $(this).css({ "z-index": 80 });
        $(this).find('nav').fadeOut(300);
        if (SS.action["focus"] == id) {
            SS.action["focus"] = "";
        }
    }, timeout: 500});
    
    
    $("#inspection_" + id).find("nav")
    
    return objdiv;
};

SimpleSeer.Frame = {};


SimpleSeer.Frame.refresh = function() {
    SimpleSeer.framecount = SimpleSeer.getValue('framecount');

    SimpleSeer.inspections = SimpleSeer.getJSON('inspections');
    SimpleSeer.measurements = SimpleSeer.getJSON('measurements');
    SimpleSeer.results = SimpleSeer.getJSON('results');
    SimpleSeer.histogram = SimpleSeer.getJSON('histogram_0');
   
    SS.Feature.refresh();
    SS.histgraph.draw();
    $(".object").remove();
    $("#maindisplay").find("img").attr("src", "/GET/currentframe_0.jpg?" + new Date().getTime().toString());    
};


SimpleSeer.Frame.capture = function() {
    $.post("/frame_capture", {}, function(data) {
        SS.Frame.refresh();
        if (SS.continuousCapture) {
            SS.Frame.capture();
        }
    });
    return false;
}


SimpleSeer.Frame.inspect = function() {
    $.post("/frame_capture", {}, function(data) {
        SS.Frame.refresh(); })
    
    return false;
}


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
            SS.inspections = data; 
            SS.Frame.refresh();
            SS.Inspection.cancelPreview();

            });
};

SimpleSeer.Inspection.preview = function (method, parameters) {
    if (SS.preview_running) {
        SS.preview_queue = [method, parameters];
        return; //if there's already a preview running on this screen, wait
    }
    
    SS.preview_queue = [];
    SS.preview_running = true;
    $.post("/inspection_preview", { name: "preview", camera: SS.framedata[0].camera, method: method, parameters: JSON.stringify(parameters)},
        function(data) {   
            if ("halt" in SS.preview_data) {
                SS.preview_data = {};
            } else {
                SS.preview_data = data;
            }
            SS.preview_running = false;
            });
}

SimpleSeer.Inspection.cancelPreview = function () {
    SS.preview_queue = [];
    if (SS.preview_running) {
        SS.preview_data["halt"] = true;
    } else {
        SS.preview_data = {};
    }
}

SimpleSeer.Inspection.render = function() {
    //render any active inspections
    for (i in SS.inspections) {
        insp = SS.inspections[i];
        if (insp["method"] in SS.inspectionhandlers) {
            SS.inspectionhandlers[insp["method"]].render(insp); 
        }
    }
    
    //render any active previews
    if (!isEmpty(SS.preview_data)) {
        pv = SS.preview_data;
        if (pv.inspection.method in SS.inspectionhandlers) {
            SS.inspectionhandlers[pv.inspection.method].render_features(pv.features, pv.inspection)
        }
    }
    
    
};

SimpleSeer.Inspection.remove = function(insp) {
    if (insp["method"] in SS.inspectionhandlers && "remove" in SS.inspectionhandlers[insp["method"]]) {
        SS.inspectionhandlers[insp["method"]].remove(insp);
    } 
    
    SS.action.task = "inspection_remove";
    if (SS.action.focus == "inspection_" +insp.id) {
        SS.action.focus = "";
    }
    
    $.post("/inspection_remove", { id: insp.id }, function(data) {
        SS.inspections = data;
        SS.resetAction();           
    });
};


SimpleSeer.Inspection.control = function(insp, x, y) {
    
    var div_id = "inspectioncontrol_" + insp.id;
    
    if ($("#" + div_id).length > 0) {
        if (insp.method in SS.inspectionhandlers && "updatecontrol" in SS.inspectionhandlers[insp.method]) {
            SS.inspectionhandlers[insp.method].updatecontrol(insp);
        }
        return;
    }
    
    $("#maindisplay").append($("<div/>", { id: div_id, class: "inspectioncontrol" }));
    
    if (insp.method in SS.inspectionhandlers && "rendercontrols" in SS.inspectionhandlers[insp.method]) {
        SS.inspectionhandlers[insp.method].rendercontrols(insp, div_id);
    }
    
    point = [0,0];
    //TODO, find the view area if we are zoomed in

    if (x == undefined) {
        point[0] = $("#maindisplay").width() - $(div_id).width();
        point[1] = $("#maindisplay").height() / 2 - $(div_id).height() / 2;
    } else {
        point = SS.imageToProcessingCoordinates(x,y);
    }
    $("#" + div_id).css({ top: point[0].toString() + "px", left: point[1].toString() + "px"}).draggable().hover( function() {
                SS.mouseBlock = true;
            }, function() {
                SS.mouseBlock = false;
            });
};

SimpleSeer.Inspection.findMeasurement = function(inspection, featurecriteria, method) {
    for (i in SS.measurements) {
        measurement = SS.measurements[i];
        if (measurement.inspection == inspection.id &&
            measurement.method == method &&
            _.isEqual(featurecriteria, measurement.featurecriteria)) {
            return measurement;
        }
        
    }
    return null;
}



SimpleSeer.InspectionControl = {};

SimpleSeer.InspectionControl.controlBox = function(id, title, controls) {
    cb = $("<div/>", { id: id, class: "controlblock"}).append(title);
    
    if (controls != undefined) {
        for (i in controls) {
            cb.append(controls[i]);   
        }
    }
    
    return cb;
}


SimpleSeer.InspectionControl.checkbox = function(id, param, label, checked, onchange) {
    return $("<div/>", { class: "control" }).append(
        $("<input/>", { id: id, type: "checkbox"}).change(onchange)
    ).append(
        $("<label/>", { for: id }).append(label).css({ right: "0px" })
    );
}

SimpleSeer.InspectionControl.slider = function(id, param, title, defaultval, min, max, step, onchange) {
    return $("<div/>", { class: "control" }).append(
        $("<label/>", { for: id  }).append(title)
    ).append(
        $("<div/>", { id: id }).css({ height: "10px", width: "100%" }).slider({
            value: defaultval,
            min: min,
            max: max,
            step: step,
            slide: onchange})
    );
};

SimpleSeer.InspectionControl.button = function(id, title, onclick) {    
    return $("<div/>", { class: "control" }).append(
        $("<button/>", { id: id }).append(title).button().click(onclick)
    );
};

SimpleSeer.InspectionControl.applyCancelButton = function(id, onapply, oncancel) {  
    
    return $("<div/>", { class: "control" }).append(
        $("<button/>", { id: id }).append("Apply").button().click(onapply)
    ).append(
        $("<button/>", { id: id }).append("Cancel").button().click(oncancel)
    );  
};

SimpleSeer.InspectionControl.cancelButton = function(id) {
    return SS.InspectionControl.button(id, "Cancel", function(e) {
    
    });
};

SimpleSeer.InspectionControl.rangeSlider = function(id, param1, param2, title, default1, default2, min, max, step, onchange) {
    return $("<div/>", { class: "control" }).append(
        $("<label/>", { for: id  }).append("title")
    ).append(
        $("<div/>", { id: id }).slider({
            range: true,
            values: [default1, default2],
            min: min,
            max: max,
            step: step,
            slide: onchange})
    );
};


SimpleSeer.InspectionControl.histogramSlider = function(id, param1, title, histogram, min, max, step, onchange) {
    
    
};

//SimpleSeer.InspectionControl.addSelect

//SimpleSeer.InspectionControl.addNumber = function




SimpleSeer.Feature = {};

SS.Feature._mapFeaturesets = function(feat) {
    if (feat.inspection in SS.featuresets) {
        SS.featuresets[feat.inspection].push(feat);
    } else {
        SS.featuresets[feat.inspection] = [ feat ];
    }
    
    for (i in feat.children) {
        SS.Feature._mapFeaturesets(feat.children[i]);
    }
}



SimpleSeer.Feature.refresh = function() {
    SimpleSeer.framedata = [SimpleSeer.getJSON('currentframedata_0')];
    //build a hash of inspection_id -> featureset
    SimpleSeer.featuresets = {};
    for (i in SS.framedata[0].features) {
        SS.Feature._mapFeaturesets(SS.framedata[0].features[i]);
    }
}


SimpleSeer.Feature.render = function() {
    for (i in SS.inspections) {
        insp = SS.inspections[i];
        
        if (insp.method in SS.inspectionhandlers 
           && 'render_features' in SS.inspectionhandlers[insp.method]
           && SS.featuresets[insp.id]) {
            SS.inspectionhandlers[insp.method]["render_features"](SS.featuresets[insp.id], insp);
        } else {
                
        }
        
    }
    
    
}

SimpleSeer.Measurement = {};

SimpleSeer.Measurement.add = function(params) {
    //name, label, units, featurecriteria, method, parameters, inspection
    if (!("name" in params)) {
        params.name = params.inspection.name + " " + params.method;
    }
    
    if (!("label" in params)) {
        params.label = params.method.charAt(0).toUpperCase() + params.method.slice(1)
    }
    
    if ("featurecriteria" in params) {
        params.featurecriteria = JSON.stringify(params.featurecriteria);
    } else {
        params.featurecriteria = '{}';
    }
    
    if ("parameters" in params) {
        params.parameters = JSON.stringify(params.parameters);
    } else {
        params.parameters = '{}';
    }
    
    params.inspection = params.inspection.id;
    
    $.post("/measurement_add", params, 
        function(data) { 
            SS.measurements = data; 
            SS.Frame.refresh();
        });
}



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


SS.p.setup = function() {
  SS.p.size($('#maindisplay > img').width(), $('#maindisplay > img').height());
  SS.resetAction();
}

//to/from functions to map canvas and image.  We have to include a special factor
//for zooming
SS.processingToImageCoordinates = function(x, y) {
    return [Math.round(x / (SS.xscalefactor * SS.zoomer.zoomLevel())), 
        Math.round(y / (SS.yscalefactor * SS.zoomer.zoomLevel()))];
    
}

SS.imageToProcessingCoordinates = function(x, y) {
    return [Math.round(x * (SS.xscalefactor * SS.zoomer.zoomLevel())), 
        Math.round(y * (SS.yscalefactor * SS.zoomer.zoomLevel()))];
}

SS.setScale = function() {
  SS.p.scale(SS.xscalefactor, SS.yscalefactor);
  
  mousePoints = SS.processingToImageCoordinates(SS.p.mouseX, SS.p.mouseY);
  SS.mouseX = mousePoints[0];
  SS.mouseY = mousePoints[1];
}


//these get registered to with each handler
SS.inspectionhandlers = {
    
    default: {

    },
    
    face: {
        render_features: function(feats, insp) {
            SS.p.stroke(255, 0, 0, 75);
            SS.p.strokeWeight(6);
            SS.p.noFill();
            

            
            for (i in feats) {
                f = feats[i];
                SS.p.rect(f.points[0][0], f.points[0][1], f.width, f.height, 6);
            
                div_id = "inspection_" + insp.id + "_" + i.toString();

                inspdiv = SS.Display.addDisplayObject(div_id, f.points[0][0], f.points[0][1], f.width, f.height);
                SS.DisplayObject.addNavZoomIn(div_id); 
                SS.DisplayObject.addNavZoomOut(div_id);
            }
            
            
        },
        
        render: function(insp) {
            
        
        }
    },
    region: {
        render: function(insp) {
            if (SS.action["focus"] != "inspection_" + insp.id) {
                SS.p.fill(255, 255, 255, 20);
            } else {
                SS.p.noFill();
            }
            SS.p.stroke(0);
            p = insp.parameters;
            SS.p.rect(p.x, p.y, p.w, p.h);
            id = insp.id;

            zoomlevel = SS.zoomer.zoomLevel();
            
            feat = SS.featuresets[id].inspection;

            if ($("#inspection_" + id).length){
                return;
            }
            
            div_id = "inspection_" + id;
            inspdiv = SS.Display.addDisplayObject(div_id, p.x, p.y, p.w, p.h);

            SS.DisplayObject.addNavZoomIn(div_id); 
            SS.DisplayObject.addNavZoomOut(div_id);
            SS.DisplayObject.addNavInfo(div_id, "Region Properties", {
                x: { label: "top", units: "px" },
                y: { label: "left", units: "px"},
                width: { label: "width", units: "px"},
                height: { label: "height", units: "px"},
                meancolor: { label: "color", handler: function(clr) { 
                    clrhex = [];  
                    for (i in clr) { clrhex.push(Math.round(clr[i]).toString(16)); } 
                    return "#" + clrhex.join("");
                    }, units: ""}
                }, insp, 0);
            SS.DisplayObject.addNavItem(div_id, "close", "Remove", function(e) {
                SS.Inspection.remove(insp);
                SS.mouseBlock = false;
                return false;
            });
            
            
        },
        
        remove: function(insp) {
            $("#inspection_" + insp.id).remove();
            SS.waitForClick();
        },
        render_features: function(feats, insp) {
            
            
            
            
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
            SS.p.stroke(0);
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
    }
    
};

//interface helpers, functions to control aspects of interface state
SS.launchRadial = function(animate) {
    
    if (SS.radialAnimating) {
        return;
    }
    oldtask = SS.action["task"];
    
    radius = 110;
    offset = SS.zoomer.offset();
    
    if (oldtask == "radial_select") {
        distance = SS.xscalefactor * SS.euclidean(SS.action["startpx"], [SS.mouseX, SS.mouseY]);
        if (distance > 75 && animate) { 
            SS.radialAnimating = true;
            $("#radial_container").animate( {
                top: (SS.p.mouseY - radius - offset[1]).toString() + "px", 
                left: (SS.p.mouseX - radius - offset[0]).toString() + "px" }, 300,
                function() { SS.radialAnimating = false; } 
            );    
        } else {
            $("#radial_container").css( {
                top: (SS.p.mouseY - radius - offset[1]).toString() + "px", 
                left: (SS.p.mouseX - radius - offset[0]).toString() + "px" 
            });   
        }   
    } else {
        $("#radial_container").radmenu("show").css( { zIndex: 99,
            top: (SS.p.mouseY - radius - offset[1]).toString() + "px", 
            left: (SS.p.mouseX - radius - offset[0]).toString() + "px" } );
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
          if (SS.mouseDown && "manipulate_onclick" in SS.inspectionhandlers[task]) {
              SS.inspectionhandlers[task].manipulate_onclick();
          } else {
              SS.inspectionhandlers[task].manipulate();
          } 
          //or manipulate onclick
      }
  } 
  SS.Inspection.render();
  SS.Feature.render();  
  if (SS.mouseDown && !SS.mouseWait) {
      if (SS.wasPressed) {
        SS.launchRadial();
      } else {
        SS.launchRadial(true);   
      }
  } 

  
  if (SS.action.focus) {
      SS.Display.renderObjectFocus(SS.action.focus);
  }
  
  if (SS.preview_queue.length && SS.preview_queue.length == 2) {
      SS.Inspection.preview(SS.preview_queue[0], SS.preview_queue[1]);
  }
  
  
  SS.wasPressed = SS.mouseDown;
 
}


//TODO PUT ALL THESE in a "STATEMACHINE" object that gets backed up to redis
//import some context from webdis, 
SimpleSeer.cameras = SimpleSeer.getJSON('cameras');
SimpleSeer.preview_running = false;
SimpleSeer.preview_data = {};
SimpleSeer.preview_queue = [];

SimpleSeer.poll_interval = parseFloat(SimpleSeer.getValue('poll_interval'));



SimpleSeer.featuresets = {};








SimpleSeer.radialAnimating = false;

SS.continuousCapture = false;

SS.wasPressed = false;


SimpleSeer.waitForClick = function() {
    if (SS.mouseDown) {
        SS.mouseWait = true;
    }
}

SimpleSeer.resetAction = function() {
    SS.action = { startpx: [0,0], task: "", focus: "" };
}

SimpleSeer.loadPlugins = function() {
    
}



//initalize the display and the resize function
//TODO add any other independent behaviors
$(function(){

    var stretcher = $('#maindisplay').find('img'),
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
SimpleSeer.setup = function() { $.getScript("/plugin_js", function(){
    SS.p.setup();
    SS.p.loop();
    SS.zoomer = zoom($("#zoomer")[0]);
    SS.loadPlugins();


    SS.histgraph.setup();


    SS.mouseBlock = false;
/* these functions just give us a little extra context for when processing doesn't pick up events*/
   $("#maindisplay").mousedown( function(e) {
      if (SS.mouseBlock) {
        return;
      } 
      SS.mouseDown = true;
   });

   $("#maindisplay").mouseup( function(e) {
      if (SS.mouseBlock) {
        return;
      } 
      
      SS.mouseDown = false;
      SS.mouseWait = false; 
   });

   $("#maindisplay").mousemove(function(e) {
  //SS.setScale();
    if (SS.mouseBlock) {
        return;
    } 
    
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


   $(".ico.play").click( SS.Frame.capture );


   SimpleSeer.Frame.refresh();

})};


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
}

SS.histgraph.draw = function() {
    h = SS.histgraph;

    h.background(0,0);
    h.stroke(255);

    h.yscalefactor =  h.height / Math.max.apply(Math, SS.histogram);
    h.xstep = h.width / SS.histogram.length;
    
    for (i in SS.histogram) {
        x = h.xstep * i + 1;
        y = SS.histogram[i] * h.yscalefactor;
        
        h.line(x, h.height, x, h.height - y);
    }
}

