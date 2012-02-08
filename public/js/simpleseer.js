
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

SimpleSeer.DashObject = {};

SimpleSeer.DashObject.add = function(inspection, fadein){
    if (fadein == undefined) {
        fadein = 300;
    }
    $("#statebar").append(
        $("<li/>", {
            id: "dash_" + inspection.id,
            class: "dashobject"
        }).append(inspection.name).fadeIn(fadein).hoverIntent({
            over: function(){
                $(this).addClass("dashobject-hover");
            }, out: function(){
                $(this).removeClass("dashobject-hover");
            }, timeout: 100})
        );
};

SimpleSeer.DashObject.remove = function(inspection) {
    
};

SimpleSeer.DashObject.refresh = function() {
    $(".dashobject").remove();
    for (i in SS.inspections) {
        SS.DashObject.add(SS.inspections[i], 0);    
    }
};

SimpleSeer.DisplayObject = {};

SimpleSeer.DisplayObject.setFocus = function(id) {
    if (SS.action.focuslock) {
        return;
    }
    $("#" + id).css({ "z-index": 99 }).find('nav').fadeIn(200);    
    SS.action.focus = id;
    index = SS.Inspection.getIndex(id.split("_")[1]);
    $.getJSON("/histogram?focus=" + index.toString(), function(data) {
        SS.histgraph.newHistogram(data);      
    });
}

SimpleSeer.DisplayObject.loseFocus = function(id) {
    if (SS.action.focuslock) {
        return;
    }
    $("#" + id).css({ "z-index": 80 }).find('nav').fadeOut(300);
    if (SS.action.focus == id) {
        SS.action.focus = "";
        SS.histgraph.newHistogram();   
    }
}

SS.DisplayObject.lockFocus = function(id) {
    if (SS.action.focus != id) {
        SS.DisplayObject.setFocus(id);
    }
    SS.action.focuslock = true;
}

SS.DisplayObject.unlockFocus = function() {
    SS.action.focuslock = false
}




SimpleSeer.DisplayObject.addNavItem = function(id, iconcls, title, clickmethod) {
    //TODO, when nav is close to right side, flip to left-nav (css class)
    
    $("#" + id).find("nav").append(
       $("<a/>", { title: title, href: "#" }).append(
            $("<b/>", { class: "ico " +iconcls })
        ).click(clickmethod).tooltip({
            position: "right" ,
            offset: [0, -10],
            predelay: 200,
            effect: "fade"}
        ).dynamic({right: { direction: "left" }})
    );
}

SimpleSeer.DisplayObject.addNavZoom = function(id) {
    SS.DisplayObject.addNavItem(id, "zoom-in", "Zoom In on this Region", function(e) {
        
        icon = $(e.target);
        if (icon.hasClass("zoom-in")) {
            icon.removeClass("zoom-in").addClass("zoom-out");
            SS.zoomer.in( { element:$(e.target).parent().parent().parent()[0] } );
        } else {
            icon.removeClass("zoom-out").addClass("zoom-in");
            SS.zoomer.out();
        }
        
        SS.mouseBlock = false;
        return false;
    });
}


SimpleSeer.DisplayObject.addNavLock = function(id) {
    SS.DisplayObject.addNavItem(id, "unlock", "Lock Focus on this Region", function(e) {
        icon = $(e.target);
        if (icon.hasClass("lock")) {
            icon.removeClass("lock").addClass("unlock");
            SS.DisplayObject.unlockFocus();
        } else {
            icon.removeClass("unlock").addClass("lock");
            SS.DisplayObject.lockFocus(icon.parent().parent().parent().attr('id'));
            //TODO, will only work for region right now.  need to come up with a more
            //generalizable object id lookup
        }
        
        return false;
    });
}




SimpleSeer.DisplayObject.addNavInfo = function(id, title, info, inspection, featureindex) {
    SS.DisplayObject.addNavItem(id, "info", "View Attributes of this Region", function(e) {
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
    }).mouseup(function() {
        $(window).mouseup(); 
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
        SS.DisplayObject.setFocus($(this).attr('id'));

    }, out: function(){
        SS.DisplayObject.loseFocus($(this).attr('id'));
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
    SS.DashObject.refresh();
    SS.histgraph.newHistogram();
    $(".object").remove();
    $(".tooltip").remove();
    $("#maindisplay").find("img").attr("src", "/GET/currentframe_0.jpg?" + new Date().getTime().toString());
    SS.p.refresh();
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
};



//functions to deal with adding/previewing/updating/deleting models
SimpleSeer.Inspection = {}

SimpleSeer.Inspection.getIndex = function(id) {
    for (i in SS.inspections) {
        if (SS.inspections[i].id == id) {
            return i;
        }  //TODO, need to crawl children as well
    }
    
    return undefined;
};

SimpleSeer.Inspection.fromId = function(id) {
    return SS.inspections[SS.Inspection.getIndex(id)];
}



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

SimpleSeer.Inspection.update = function(inspection){
    $.post("/inspection_update", {
        id: inspection.id,
        name: inspection.name,
        parameters: JSON.stringify(inspection.parameters)
    },function(data) {
        SS.inspections = data;
        SS.Frame.refresh();
        SS.Inspection.cancelPreview();
    });   
}


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
        SS.Frame.refresh();       
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
    $("#" + div_id).css({ top: point[0].toString() + "px", left: point[1].toString() + "px"}).draggable();
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
    attrs = { id: id, type: "checkbox"};
    if (checked) {
        attrs.checked = "";
    }
    
    return $("<div/>", { class: "control" }).append(
        $("<input/>", attrs).change(onchange)
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
    }
};

//interface helpers, functions to control aspects of interface state
//TODO - make icons bigger
//TODO figure out why titles aren't hovering (hover() does work)
//TODO choose relevant icons

SS.radial_actions = ["region", "blob", "", ""];

$("#maindisplay").prettypiemenu({
    buttons: [
        { img: "smico crop", title: "Select a Region" }, 
        { img: "smico contrast",  title: "Find a light or dark Object" },
        { img: "smico sliders",  title: "Find an Object by color" },
        { img: "smico bright", title: "Look for Movement" },
        { img: "smico chat",  title: "Leave an Annotation" },
        { img: "smico info", title: "View Attributes" },
    ],
    iconW: 30,
    iconH: 30,
    outerPadding: 100,
    showAnimationSpeed: 250,
    closeRadius: 5,
    onSelection: function (index) {
        SS.action.task = SS.radial_actions[index];
    },
    showTitles: true
});




SS.launchRadial = function() {
    //SS.action.task = "radial_select";
    SS.action.startpx = [SS.mouseX, SS.mouseY];
    $("#maindisplay").prettypiemenu("show", {top: SS.p.mouseY, left: SS.p.mouseX});
}


SS.p.render = function() {
    
    SS.p.background(0, 0); 
      
        
    SS.Inspection.render();
    SS.Feature.render();  
  
    task = SS.action.task;
        
    if (task in SS.inspectionhandlers) {
        if (SS.mouseDown && "manipulate_onclick" in SS.inspectionhandlers[task]) {
            SS.inspectionhandlers[task].manipulate_onclick();
        } else {
            SS.inspectionhandlers[task].manipulate();
        } 
        //or manipulate onclick
    }
    
    if (SS.action.focus) {
        SS.Display.renderObjectFocus(SS.action.focus);
    }
    
    if (SS.preview_queue.length && SS.preview_queue.length == 2) {
        SS.Inspection.preview(SS.preview_queue[0], SS.preview_queue[1]);
    }

};


SS.p.refresh = function () {
    SS.forcerender = true;
};

SS.p.mouseReleased = function() {
    $(window).mouseup();
}


//the draw function is the loop() it can be enabled and disabled with SS.p.noLoop()
SS.p.draw = function() {
  SS.setScale();


  if (!SS.action.task && SS.mouseDown && !SS.mouseWait) {
      if (!SS.wasPressed) {
        SS.launchRadial();
      } 
  }
  
  SS.wasPressed = SS.mouseDown;



  if (SS.action.task ||
      (SS.preview_queue.length && SS.preview_queue.length == 2) ||
      SS.action.focus != SS.lastfocus ||
      SS.forcerender) {
      
      SS.p.render();
      SS.forcerender = false;
      SS.lastfocus = SS.action.focus;
  }

  
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
SS.forcerender = false;

SS.wasPressed = false;
SS.lastfocus = "";


SimpleSeer.waitForClick = function() {
    if (SS.mouseDown) {
        SS.mouseWait = true;
    }
}

SimpleSeer.resetAction = function() {
    SS.action = { startpx: [0,0], task: "", focus: "", focuslock: false, update: "" };
    SS.p.refresh();

}

SimpleSeer.loadPlugins = function() {
    $.getScript("/plugin_js");
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
        SS.p.refresh();
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


    SS.histgraph.setup();


    SS.mouseBlock = false;
/* these functions just give us a little extra context for when processing doesn't pick up events*/
   $("#maindisplay").mousedown( function(e) {
      if (SS.mouseBlock) {
        return;
      } 
      SS.mouseDown = true;
   });

   
   $(window).mouseup( function(e) {
      if (SS.mouseBlock) {
        return;
      } 
      
      SS.mouseDown = false;
      SS.mouseWait = false;
      $("#maindisplay").prettypiemenu("hide");
   });

   $("#maindisplay").mousemove(function(e) {
  //SS.setScale();
    if (SS.mouseBlock) {
        return;
    } 
    
    $("#maindisplay").prettypiemenu("_changeHighlight", e);
    SS.p.mouseX = e.pageX - $("#display").offset()["left"];
    SS.p.mouseY = e.pageY - $("#display").offset()["top"];
   
   
   });

   $(".btngrp").find("a").tooltip({
        position: "top" ,
        offset: [0, -10],
        predelay: 200,
        effect: "fade"}
    ).dynamic({right: { direction: "left" }})
   $(".ico.play").click( SS.Frame.capture );
    


   SimpleSeer.Frame.refresh();
   SS.p.render();

})};


//histogram
SS.histgraph = new Processing("histogram");

SS.histgraph.setup = function() {
    h = SS.histgraph;
    h.size(150, 48);
    h.last = "";
    h.hist = [];
    h.maxstep = 12;
    h.frameRate(20);
    h.step = 0;
    //h.noLoop();
    h.stroke(255);
    h.strokeCap(h.PROJECT);
};

SS.histgraph.newHistogram = function(hist) {
    h = SS.histgraph;
    h.step = 0;
    if (!hist) {
        h.hist = SS.histogram;
        if (!h.last) {
            h.last = SS.histogram;   
        }
    } else {
        h.hist = hist;
    }
    
    h.oldscalefactor =  h.height / Math.max.apply(Math, h.last);
    h.newscalefactor =  h.height / Math.max.apply(Math, h.hist);
    if (!h.oldscalefactor) {
        h.oldscalefactor = 1;
    }
    h.loop();
}


SS.histgraph.draw = function() {
    h = SS.histgraph;
    if (!SS.histogram) {
        return;
    }
    
    h.background(0,0);
    var hist = new Array(h.hist.length)

 
    
    for (i in h.hist) {
        diff = h.maxstep - h.step;
        hist[i] = (h.step / h.maxstep) * h.hist[i] * h.newscalefactor +
            (diff / h.maxstep) * h.last[i] * h.oldscalefactor;
    }  
    
   if (h.step == h.maxstep) {
        h.noLoop();
        h.last = h.hist;
        h.step = 0;
    }
    h.xstep = h.width / hist.length;
    h.strokeWeight(h.xstep -1);

    
    for (i in hist) {
          x = h.xstep * i + 1;
          y = hist[i];
          h.line(x, h.height, x, h.height - y);
    }
    h.step++;
}

