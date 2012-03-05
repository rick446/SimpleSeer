//TODO: port all models, collections to backbone
//TODO: segment by function
//TODO: see if my helpers can be replaced with underscore



isEmpty = function(obj) {
    for (var prop in obj) {
        if (obj.hasOwnProperty(prop)) return false;
    }
    return true;
};

//http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript
capitalize = function(word){
   return word.replace( /(^|\s)([a-z])/g , function(m,p1,p2){ return p1+p2.toUpperCase(); } );
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
//TODO, get multiple values
//TODO, optimize with a websocket to webdis: possible with nginx?
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


//TODO make the dashboard flexible so it can be moved
//from top or side, depending on display mode (portrait or landscape)
SimpleSeer.DashObject = {};

$("#statebar").hoverIntent({
    over: function() {},
    out: function() {
        dashnav = $(this).find(".dashobject-nav");
        if (dashnav.length) {
            dashobj = dashnav.parent();
            dashobj.css({
                "border-radius": 4 
            });
            dashobj.find(".dashobject-nav").animate({
                width: 1
            }, 400, function() { $(this).remove(); });
            dashobj.animate({
                left: 0
            }, 300, function() { $(this).css( {left: ""} )});
            dashobj.prevAll().animate({
                left: 0
            }, 300, function() { $(this).css( {left: ""} ) });
            dashobj.nextAll().animate({
                right: 0 
            }, 300, function() { $(this).css( {right: ""} ) });
        
            $(".dashobject").removeClass("dashobject-hover");
            SS.action.highlight = "";
            SS.p.refresh();
        }
    }
})

//TODO break out rendering of objects from their insertion
//TODO be sensitive to other objects occupying the dash space
//TODO make the dashobjects themselves more informative (sparklines?)
SimpleSeer.DashObject.add = function(inspection, fadein){
    if (fadein == undefined) {
        fadein = 300;
    }
    $("#statebar").append(
        $("<div/>", {
            id: "dash_" + inspection.id,
            class: "dashobject"
        
        }).append(inspection.name).append(
            $("<div/>", 
                { class: "dashobject-summary" }).append(SS.Inspection.summary(inspection))
        ).fadeIn(fadein).hoverIntent({
            over: function(){
                $(this).addClass("dashobject-hover");
                SS.action.highlight = $(this).attr('id').split("_")[1];
                SS.p.refresh();
                
            }, 
            out: function(){
                if ($(this).find(".dashobject-nav").length) {
                    return;
                }
                $(this).removeClass("dashobject-hover");
                if (SS.action.highlight == $(this).attr('id').split("_")[1]) {
                    SS.action.highlight = "";
                }
                console.log("no highlight");
                SS.p.refresh();
            }, timeout: 300}
        ).click(function() {
            dashnav = $(this).find(".dashobject-nav");
            if (dashnav.length) {
                return;
            }
            $(this).addClass("dashobject-hover");
            var target = this;
            var insp_id = $(target).attr("id").split("_")[1];
            SS.action.highlight = "";
            //TODO, figure out how to give (lock?) and when to release focus.
            $(this).css({
                "border-radius": "4px 0px 0px 4px"
            });
            $(this).animate({
                left: -$(this).offset().left + 12
            }, 400, function() {
                $(target).append(
                    $("<div/>", { class: "dashobject-nav", id: "dashnav_" + insp_id }).css({
                        "z-index": -1,
                        left: 0,
                        height: $(this).height(),
                        top: -2
                    }).animate({
                        left: $(this).outerWidth() - 4,
                        width: $(this).parent().width() * .75 
                    })
                );
                console.log($(target).attr("id"));
                insp = SS.Inspection.fromId($(target).attr("id").split("_")[1]);
                dashboard = SS.Inspection.fetchHandler(insp, "dashboard");
                dashboard(insp);
            });
            $(this).prevAll().animate({ left: -2000 }, 800); 
            $(this).nextAll().animate({ right: -2000 }, 800);
        })
    )
    

};

//TODO implement this rather than just re-creating all the dash objects
SimpleSeer.DashObject.remove = function(inspection) {
    
};

SimpleSeer.DashObject.refresh = function() {
    $(".dashobject").remove();
    for (i in SS.inspections) {
        SS.DashObject.add(SS.inspections[i], 0);    
    }
    dobjs = $("#statebar > .dashobject");
    var minwidth = 50;
    dobjs.each(function(index) { if ($(this).width() > minwidth) { minwidth = $(this).width(); } });
    dobjs.css("width", minwidth + "px"); //align width on all of them
};



SimpleSeer.DisplayObject = {};


//TODO make all actions inside an object focus respect the focus
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
};


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


//TODO align this when the inspection's dashobject is expanded
SS.DisplayObject.lockFocus = function(id) {
    if (SS.action.focus != id) {
        SS.DisplayObject.setFocus(id);
    }
    SS.action.focuslock = true;
}

SS.DisplayObject.unlockFocus = function() {
    SS.action.focuslock = false
}


SimpleSeer.navItem = function(title, iconcls, clickmethod) {
    return $("<a/>", { title: title, href: "#" }).append(
        $("<b/>", { class: "ico " +iconcls })
    ).click(clickmethod).tooltip({
        position: "right" ,
        offset: [0, -10],
        predelay: 200,
        effect: "fade"}
    ).dynamic({right: { direction: "left" }});
};


SimpleSeer.DisplayObject.addNavItem = function(id, iconcls, title, clickmethod) {
    //TODO, when nav is close to right side, flip to left-nav (css class)
    
    $("#" + id).find("nav").append(
       SS.navItem(title, iconcls, clickmethod)
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

//TODO, can we reuse this on dash objects
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

//TODO consolidate this with the other watchlist stuff
//only real difference is sparkline and contextual independence
SimpleSeer.DisplayObject.addNavInfo = function(id, title, inspection, featureindex) {
    feature_measurements = SS.Inspection.fetchHandler(inspection, "feature_measurements");
    info = feature_measurements();
    
    SS.DisplayObject.addNavItem(id, "info", "View Attributes of this Region", function(e) {
        $(e.target).parent().parent().find(".detail").fadeIn(300);
        return false;
    });
    
    watchlist = $("<div/>", { class: "detail" }).append(title);
    for (prop in info) {
        value = SS.featuresets[inspection.id][featureindex][prop];
        
        watchlist.append(
            SS.Watchlist.renderItem(info[prop], value, prop, inspection, { index: featureindex })
        );
    }
    
    $("#" + id).find("nav").append(watchlist)
}

SimpleSeer.Watchlist = {};

//TODO: make this additive, so we're not re-rendering everything
SimpleSeer.Watchlist.refresh = function() {
    watchlist =$(".watchlist"); 
    if (!watchlist.length) {
        return; 
    }
    watchlist.html(SS.Watchlist.renderWatchedItems());
    SS.Watchlist.renderSparklines();
};

//TODO, respect other items in the dashboard space 
SimpleSeer.Watchlist.showWatchedItems = function(){
    /*$("#statebar > .dashobject").animate({
        left: -999
    });*/
    $("#statebar").append(
        $("<div/>", {class: "watchlist"}).css({
            right: -3000
        }).append(
            SS.Watchlist.renderWatchedItems()
        ).animate({
            right: 0
        })
    );
    SS.Watchlist.renderSparklines();
};

//Do we really need this?
SimpleSeer.Watchlist.hideWatchedItems = function() {
    $(".watchlist").animate({
        right: -3000
    }, 600, function() {
        $(this).remove();
    });
    /*$("#statebar > .dashobject").animate({
        left: 0
    }, 600, function(n) {
        $(this).css( { left: '' } );
    });*/
};

SimpleSeer.Watchlist.renderWatchedItems = function() {
    content = $("<table/>", { class: "watchlistcontent" });
    
    if (!SS.measurements.length) {
        return $("<div/>", { class: "watchlistcontent" }).append("No watched items");
    }
    
    tablecell = function(cls, i) {
        return $("<td/>", { class: cls }).append(i);
    };
    
    //TODO group these by feature and de-dupe insp labels on the same feature
    for (i in SS.measurements) {
        m = SS.measurements[i];
        insp = SS.Inspection.fromId(m.inspection);
        value = "";
        
        result =  SS.Result.forLastFrame({ measurement: m });
        
        if (!result) {
            continue;
        }
        
        value = SS.Result.value(result, m);
        
        label = "";
        if (m.featurecriteria && m.featurecriteria.index != undefined) {
            label = insp.name + " (" + m.featurecriteria.index + ") -  " + m.label
        } else {
            label = insp.name + " - " + m.label
        }  //TODO move this to where the measurement name is generated
        console.log(m);

        content.append(
            $("<tr/>",  { class: "measurement", id: "measurement_" + m.id }).append(
                tablecell("measurement_label", label)
            ).append(
                tablecell("measurement_graph",
                    $("<span/>", {
                        id: "measurement_graph_" + m.id,
                        class: "measurement_sparkline"
                    })
                )
            ).append(
                tablecell("measurement_value", value)
            ).append(
                tablecell("measurement_remove",
                    $("<a/>", {id: "measurementremove_" + m.id}).append("X").click(function(e) {
                        SS.Measurement.remove($(this).attr("id").split("_")[1]);
                        //SS.Watchlist.refresh();
                    })
                )
            )
        );
    }
    return content;
};

//TODO, add indications for watchers
SimpleSeer.Watchlist.renderSparklines = function() {
    $(".measurement_sparkline").each(function(i) {
        id = $(this).attr("id").split("_")[2];
        $(this).sparkline(SS.Result.data(id, 30), {
            type: "line",    
            lineColor: "#EEE",
            defaultPixelsPerValue: 5,
            width: "100px",
            spotColor: "#07C"
        });
    });  
};


//TODO, make this sync better with the Result/Measurement work that's already
//being done on the backend
SimpleSeer.Watchlist.renderInspectionItems = function(inspection) {
    inspection_measurements = SS.Inspection.fetchHandler(inspection, "inspection_measurements");
    info = inspection_measurements(inspection);
    
    return SS.Watchlist.renderItems(info, inspection);
}

SimpleSeer.Watchlist.renderItems = function(info, inspection, featurecriteria) {
    
    if (!featurecriteria) {
        featurecriteria = {};
    }
    
    watchlist = [];
    
    for (prop in info) {
        if (featurecriteria.index != undefined) {
            value = SS.featuresets[inspection.id][featureindex][prop];
        } else {
            value = SS.featuresets[inspection.id];
        }
        
        watchlist.push(
            SS.Watchlist.renderItem(info[prop], value, prop, inspection, featurecriteria)
        );
    }
    
    if (watchlist.length > 1) {
        return watchlist[0].after.apply(watchlist[0], watchlist.slice(1));
    } else {
        return watchlist[0];
    }
}

//TODO add more visual elements (such as color)
//TODO handle non-numeric types such as barcodes
SimpleSeer.Watchlist.renderItem = function(info, value, method, inspection, featurecriteria) {
    label = info.label;
    
    units = ''
    if ("units" in info) {
        units = info.units;
    } 
    
    if ("handler" in info) {
        value = info.handler(value);
    }
    
    var watchclass = "ico watch";
    
    
    //TODO make the eye toggle properly onclick
    var watchfunction = function(i, fc, m, l, u) { return function() {
        SS.Measurement.add({ inspection: i,
            featurecriteria: fc,
            method: m,
            label: l,
            units: u
        });
        return false;
    } }(inspection, featurecriteria, method, label, units);
    
    meas = SS.Inspection.findMeasurement(inspection, featurecriteria, prop);
    if (meas) {
        watchclass = "ico watched"
        watchfunction = function(m) { return function() {
            SS.Measurement.remove(m);
            return false;
        }}(meas);
    }
    
    
    return $("<p/>").append(label + ": " + value + units).append(
        $("<a/>", { href: "", title: "Watch" }).append(
            $("<b/>", { class: watchclass})
        ).click(watchfunction)
    );  
};



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

//TODO, resue display objects and change their CSS rather than
//scrapping them and re-creating them every damn time
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

//TODO, add lock so we get through an entire refresh before it happens again!
SimpleSeer.Frame.refresh = function() {
    SimpleSeer.framecount = SimpleSeer.getValue('framecount');
    SimpleSeer.inspections = SimpleSeer.getJSON('inspections');
    SimpleSeer.measurements = SimpleSeer.getJSON('measurements');
    SimpleSeer.results = SimpleSeer.getJSON('results');
    SimpleSeer.watchers = SimpleSeer.getJSON('watchers');
    SimpleSeer.histogram = SimpleSeer.getJSON('histogram_0');
    SimpleSeer.failures = SimpleSeer.getJSON("failures");
    
    oldwarnings = SS.warnings;
    SimpleSeer.warnings = SimpleSeer.getJSON("warnings");
    SimpleSeer.passed = SimpleSeer.getJSON("passed");
   
    if (SS.passed) {
        $(".tools").find(".good").removeClass("off").addClass("on");
    } else {
        $(".tools").find(".good").removeClass("on").addClass("off");
    }
    
    if (oldwarnings && oldwarnings.length < SS.warnings.length) {
        $(".tools").find(".warn").removeClass("off").addClass("on");
    } else {
        $(".tools").find(".warn").removeClass("on").addClass("off");
    }
    
    if (SS.failures) {
        $(".tools").find(".fail").removeClass("off").addClass("on");
    } else {
        $(".tools").find(".fail").removeClass("on").addClass("off");
    }
    
    SS.Feature.refresh();
    SS.DashObject.refresh();
    SS.Watchlist.refresh();
    SS.histgraph.newHistogram();
    $(".object").remove();
    //$(".tooltip").remove();
    $("#maindisplay").find("img").attr("src", "/frame?" + new Date().getTime().toString());
    SS.p.refresh();
};

//TODO, support continuous capture
SimpleSeer.Frame.capture = function() {
    $.post("/frame_capture", {}, function(data) {
        SS.Frame.refresh();

    });
    return false;
}

//MODEL SECTION
//functions to deal with adding/previewing/updating/deleting models
//TODO: convert to backbone, and share spec with the backend
//TODO, figure out how to do a python like getattr which calls into the handlers
SimpleSeer.Inspection = {};

SimpleSeer.Inspection.fetchHandler = function(insp, handlername) {
    if (insp["method"] in SS.inspectionhandlers && handlername in SS.inspectionhandlers[insp["method"]]) {
        return SS.inspectionhandlers[insp["method"]][handlername];
    } 
    return function() { return ""; };
};

SimpleSeer.Inspection.fetchHandlerByMethod = function(method, handlername) {
    if (method in SS.inspectionhandlers && handlername in SS.inspectionhandlers[method]) {
        return SS.inspectionhandlers[method][handlername];
    } 
    return function() { return ""; };
};

SimpleSeer.Inspection.fetchHandlerById = function(id, handlername) {
    insp = SS.Inspection.fromId(id);
    return SS.Inspection.fetchHandler(insp, handlername);
};


SimpleSeer.Inspection.summary = function(insp) {
    summary = SS.Inspection.fetchHandler(insp, "summary");
    return summary(insp);
};

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
        insp = SS.inspections[i];
        inspection_names[insp.name] = 1;
    } //build a table of names
    
    counter = 1;
    
    generate_name = SS.Inspection.fetchHandlerByMethod(method, "generate_name");
    nameroot = generate_name(parameters);
    
    if (!nameroot) {
        nameroot = capitalize(method);
    }
    
    name = nameroot + " " + counter.toString();
    
    while (name in inspection_names) {
        counter++;
        name = nameroot + " " + counter.toString();
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

//TODO, we gotta get this integrated with "inspector" form generation
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

//TODO, recombine the preview/update thing
//TODO, figure out how to get this loop tighter
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
        render = SS.Inspection.fetchHandler(insp, "render");
        render(insp);
    }
    
    //render any active previews
    if (!isEmpty(SS.preview_data)) {
        pv = SS.preview_data;
        render_features = SS.Inspection.fetchHandler(pv.inspection, "render_features");
        render_features(pv.features, pv.inspection);
    }
    
};

SimpleSeer.Inspection.remove = function(insp) {
    remove = SS.Inspection.fetchHandler(insp, "remove");
    remove(insp);
        
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
        updatecontrol =  SS.Inspection.fetchHandler(insp, "updatecontrol");
        updatecontrol(insp);
        return;
    }
    
    $("#maindisplay").append($("<div/>", { id: div_id, class: "inspectioncontrol" }));
    
    rendercontrols = SS.Inspection.fetchHandler(insp, "rendercontrols");
    rendercontrols(insp, div_id);
    
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

//TODO there has got to be some kind of JQuery form builder we can use here.
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
        
        if (insp.id in SS.featuresets) {
            render_features =  SS.Inspection.fetchHandler(insp, "render_features");
            render_features(SS.featuresets[insp.id], insp);
        } 
    }

};


//return a new array with the features sorted
SimpleSeer.Feature.sort = function(id, handler) {
    arr = SS.featuresets[id].slice(0);  //copy the array
    arr.sort(handler);
    
    return arr;
}

//return feature with the max
SimpleSeer.Feature.min = function(id, property) {
    if (!SS.featuresets[id].length) { return ; }
    
    
    handler = function(a, b) {
        return a[property] - b[property];
    }
    return SS.Feature.sort(id, handler)[0];
};

//find the feature with the maximum value of a property
SimpleSeer.Feature.max = function(id, property) {
    if (!SS.featuresets[id].length) { return ; }
    
    
    handler = function(a, b) {
        return b[property] - a[property];
    }
    return SS.Feature.sort(id, handler)[0];
};

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

SimpleSeer.Measurement.remove = function(m) {
    if (typeof m != "string") {
        m = m.id;
    }
    
    $.post("/measurement_remove", {id: m}, 
        function(data) { 
            response = data; 
            SS.Frame.refresh();
        });
}


SimpleSeer.Measurement.fromId = function(id) {
    for (i in SS.measurements) {
        m = SS.measurements[i];
        if (m.id == id) {
            return m;
        }
    }
    
    return;
};


SimpleSeer.Measurement.render = function() {
    
};


SimpleSeer.Result = {};

SimpleSeer.Result.value = function(result, measurement, measurement_handler) {
    if (!measurement) {
        measurement = SS.Measurement.fromId(result.measurement);
    }
    
    if (!measurement_handler) {
        measurement_handler = SS.Inspection.fetchHandlerById(measurement.inspection, "measurement_" + measurement.method);
    }
    value = measurement_handler(result);
        
    console.log(result)
    if (value == "") {
        value = result.numeric;
        if (value == "") {
            value = result.string;
        }
    }
    value = value + m.units;

    return value;        
};


SimpleSeer.Result.data = function(measurement_id, max) {
    data = [];
    
    measurement = SS.Measurement.fromId(measurement_id);
    measurement_handler = SS.Inspection.fetchHandlerById(measurement.inspection, "measurement_" + measurement.method);
    
    if (!max) {
        max = 0;
    }
    
    resultset = SS.results.slice(-max);
    for (i in resultset) {
        frame = resultset[i][0];
        for (j in frame) {
            r = frame[j];
            if (r.measurement == measurement_id) {
                val = measurement_handler(r);
                
                if (val == "") {
                    val = r.numeric;
                }
                data.push(val);
            }
        }   
    }
    
    return data;
};

SimpleSeer.Result.forLastFrame = function(selector) {
    var cls;
    var obj;
    for (k in selector) {
        cls = k;
        obj = selector[k];
    }
    
    for (i in _.last(SS.results)) {
        //framesets
        frame = _.last(SS.results)[i];
        for (j in frame) {
            r = frame[j];
            if (r[cls] == obj.id) {
                return r;
            }
        }
    }
};

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
        { img: "smico chat",  title: "Leave a Note" },
        { img: "smico info", title: "View Properties" },
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
        //TODO combine these, letting the plugin check state of SS.mouseDown itself
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
//TODO eliminate this, relying instead on native javascript events
SS.p.draw = function() {
  SS.setScale();

  if (SS.action.continuous) {
    SS.continuousUpdate();
  }

  if (!SS.action.task && SS.mouseDown && !SS.mouseWait) {
      if (!SS.wasPressed) {
        SS.stopContinuous();
        SS.launchRadial();
      } 
  }
  
  SS.wasPressed = SS.mouseDown;



  if (SS.action.task ||
      (SS.preview_queue.length && SS.preview_queue.length == 2) ||
      SS.action.focus != SS.lastfocus ||
      SS.forcerender) {
      SS.stopContinuous();
      
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

SS.forcerender = false;

SS.wasPressed = false;
SS.lastfocus = "";


SimpleSeer.waitForClick = function() {
    if (SS.mouseDown) {
        SS.mouseWait = true;
    }
}

SimpleSeer.resetAction = function() {
    SS.action = { startpx: [0,0], task: "", focus: "", focuslock: false, update: "", highlight: "", continuous: false };
    SS.p.refresh();

}

SimpleSeer.startContinuous = function() {
    $.post("/start", {}, function() {
        SS.action.continuous = true;
    });
};

SimpleSeer.stopContinuous = function() {
    if (!SS.action.continuous) {
        return;
    }
    $.post("/stop", {}, function() {
        SS.action.continuous = false;
    });
};

SimpleSeer.continuousUpdate = function() {
    if (!SS.action.continuous) {
        return;    
    }
    
    $.ajax({ url: "/GET/framecount.txt", 
        dataType: 'json',
        complete: function(data){
            if (SS.framecount != data.responseText) {
                SS.framecount = data.responseText
                SS.continuousRefresh();
            }
        }});
    
};

SimpleSeer.continuousRefresh = function() {

    $.ajax( {url: "/GET/batchframe.txt",
        dataType: 'json',
        complete: function(data) {
            batch = $.parseJSON(data.responseText);
            
            console.log(batch);
            return;
            SS.histogram = batch.histogram[0];
            SS.framedata = batch.framedata[0];
            SS.results = batch.results;
            
            SS.Feature.refresh();
            SS.DashObject.refresh();
            SS.Watchlist.refresh();
            SS.histgraph.newHistogram();  //TODO, skip if we're in focus
            $(".object").remove();
            //$(".tooltip").remove();
            SS.p.refresh();
            $("#maindisplay").find("img").attr("src", "/frame?" + new Date().getTime().toString());

            //some stuff should be focus sensitive
            
            //TODO add passes failures
            //TODO break warning handling out into a function
        }
    });
    
};



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
   $("#watchlist_control").click(function() {
        if ($(this).hasClass("watch")) {
            SS.Watchlist.showWatchedItems(); 
        } else {
            SS.Watchlist.hideWatchedItems(); 
        }
        $(this).toggleClass("watch");
        $(this).toggleClass("watched");
   });

   SimpleSeer.Frame.refresh();
   SS.p.render();
   SS.Watchlist.showWatchedItems();
   SS.Watcher.failbutton();

})};

//dash

$(document).ready(function() {
    $('.options').bind('click', function() {
        var trig, purl;
        trig = $(this).attr('title');
        purl = $(this).attr('href');
        info = $(this).next('.hidden').html();
        $('.active').removeClass('active');
        $('.dash, .dialog').remove();
        $(this).addClass('active');
        $(this).parent().parent().before('<div class="dash"><div class="content clearfix"></div></div>').show( function () {
            if (info) {$('.content').prepend(info);$('.content').find('textarea').focus();}
            else {
              $('.dash .content').load(purl + ' .maincontent', function() {
                $.ajax({ url: '/js/modernizr2.js', dataType: 'script', cache: true});
              });
            }
            $('.dash').prepend('<h1>'+trig+'</h1>');
            $('.dash').prepend('<div class="close">X</div>');
            $('.close, input[value="Cancel"]').bind('click', function() {
                $('.dash').remove();
                $('.active').removeClass('active');
                return false;
            });
            $(document).keyup(function(e) {
              if (e.keyCode == 27) { $('.close').click(); }   // esc
            });
        });
        return false;
        purl.abort();
        $(this).unbind('click');
    });
});



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


//alerts
SS.Watcher = {};

SS.Watcher.render = function() {
    watch = $("<form/>", {class: "watcher"});
    
    for (i in SS.watchers) {
        w = SS.watchers[i];
        watch.append(
            $("<input/>", { type: "text", name: "name", value: w.name })
        );
        
        for (j in w.conditions) {
            c = w.conditions[j];
            
            index = w.id + "_" + j.toString() + "_";
            
            label = $("<input/>", {type: "text", value: c.label, name: index + "label"})

            
            selectmeas = $("<select/>", { name: index + "measurement" });
            for (k in SS.measurements) {
                m = SS.measurements[k];
                val = { value: m.id };
                
                if (c.measurement == m.id) {
                    val["selected"] = "";  
                } 
                selectmeas.append(
                    $("<option/>", val).append(m.name)
                );
            }
            
            condition_ops = {
                greater_than: "more than",
                less_than: "less than"
            }; //TODO load these
            
            selectop = $("<select/>", { name: index + "method"});
            for (k in condition_ops) {
                op = condition_ops[k];
                val = { value: k };
                if (c.method == val) {
                    val["selected"] = "";
                }
                selectop.append(
                    $("<option/>", val).append(op)
                );
            }
            
            thresh = $("<input/>", {type: "text", value: c.threshold, name: index + "threshold"})
            
            watch.append("<br>").append(label).append(selectmeas).append(selectop).append(thresh);
            
            
            
        }
        
    }
    
    return watch;
}

SS.Watcher.failbutton = function() {
    $('.trig').bind('click', function() {
        var trig = $(this).attr('title');
        var purl = $(this).attr('href');
        var info = $(this).next('.hidden').html();       
        var howh = $(document).height();
        $('.splash').css('height',+howh+'px');	
        $("html, body").animate({ scrollTop: 0 }, "fast");
        $('.modal, .splash').remove();
        $('body').prepend('<span class="splash"></span>');
        $('body').prepend('<div class="modal"><div class="content clearfix"></div></div>').show('fast', function () {
            if (info) {$('.content').prepend("<H2>Configure Alerts</H2>");}
            else {
                $('.modal .content').load(purl + ' .maincontent', function() {
                    $.ajax({ url: '/js/modernizr2.js', dataType: 'script', cache: true});
                    $('input[value="Cancel"]').bind('click', function() {
                        $('.modal, .splash').remove();
                        return false;
                    });
                    $(".alerts").append(
                        SS.Watcher.render()
                    );
                });
            }
            $('.modal').prepend('<h1>Configure Alerts</h1>');
            $('.modal').prepend('<div class="close">X</div>');
            $('.close, .splash, input[value="Cancel"]').bind('click', function() {
                $('.modal, .splash').remove();
                return false;
            });    
        });
        return false;
        purl.abort();
        $(this).unbind('click');
    });
    $(document).keyup(function(e) {
      if (e.keyCode == 27) { 
          $('.close').click();
       }
    });    
    $('#message .close').bind('click', function() {
        $(this).parent().remove();
        return false;
    });    
};

