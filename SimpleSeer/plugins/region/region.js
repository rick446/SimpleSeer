SimpleSeer.inspectionhandlers.region = {
    
    render: function(insp) {
        SS.p.stroke(0);
        if (SS.action["focus"] != "inspection_" + insp.id) {
            if (SS.action.highlight == insp.id) {
                SS.p.fill(255, 255, 255, 50);
                SS.p.stroke(45);
            } else {
                SS.p.fill(255, 255, 255, 20);
            }
        } else {
            SS.p.noFill();
        }
        
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

        SS.DisplayObject.addNavLock(div_id);
        SS.DisplayObject.addNavZoom(div_id); 
        SS.DisplayObject.addNavInfo(div_id, "Region Properties", insp, 0);
        SS.DisplayObject.addNavItem(div_id, "close", "Remove this Region", function(e) {
            SS.Inspection.remove(insp);
            SS.mouseBlock = false;
            $(".tooltip").remove();
            return false;
        });
        
        
    },
    
    dashboard: function(insp) {
        dash_id = "dash_" + insp.id;
        
        div = $("#" + dash_id + " > .dashobject-nav");
        
        
        nav = $("<nav/>").append(
            SS.navItem("Remove this Region", "close", function(e) {
                SS.Inspection.remove(insp);
                SS.mouseBlock = false;
                console.log("removed inspection");
                console.log($(e.target).find(".tooltip"));
                $(".tooltip").remove();
                return false;
            })
        );
        
        div.append(nav);
        
        
        info = $("<div/>", { class: "info"} );
        div.append(info);
        
        info.append(
            SS.Watchlist.renderItem({label: "top", units: "px"}, insp.parameters.y, "y", insp)
        ).append(
            SS.Watchlist.renderItem({label: "left", units: "px"}, insp.parameters.x, "x", insp)
        ).append(
            SS.Watchlist.renderItem({label: "width", units: "px"}, insp.parameters.w, "width", insp)
        ).append(
            SS.Watchlist.renderItem({label: "height", units: "px"}, insp.parameters.h, "height", insp)
        ).append(
            SS.Watchlist.renderItem({label: "color", units: "", handler: function(clr) { 
                clrhex = [];  
                for (i in clr) { clrhex.push(Math.round(clr[i]).toString(16)); } 
                return "#" + clrhex.join("");
                }}, SS.featuresets[insp.id][0].meancolor, "meancolor", insp, { index: 0 })
        );
        
              
        /* SS.DisplayObject.addNavLock(div_id);
        SS.DisplayObject.addNavZoom(div_id); 
        SS.DisplayObject.addNavItem(div_id, "close", "Remove this Region", function(e) {
            SS.Inspection.remove(insp);
            SS.mouseBlock = false;
            return false;
        }); */  
        /* SS.DisplayObject.addNavInfo(div_id, "Region Properties", {
            x: { label: "top", units: "px" },
            y: { label: "left", units: "px"},
            width: { label: "width", units: "px"},
            height: { label: "height", units: "px"},
            meancolor: { label: "color", handler: function(clr) { 
                clrhex = [];  
                for (i in clr) { clrhex.push(Math.round(clr[i]).toString(16)); } 
                return "#" + clrhex.join("");
                }, units: ""}
            }, insp, 0); */
    },
    
    remove: function(insp) {
        $("#inspection_" + insp.id).remove();
        SS.waitForClick();
    },
    render_features: function(feats, insp) {
        
        
        
        
    },
    summary: function(insp) {
        p = insp.parameters;
        return p.w + "x" + p.h + " at (" + p.x + "," + p.y + ")";
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
    },
    
    feature_measurements: function() {
         return {
            x: { label: "top", units: "px" },
            y: { label: "left", units: "px"},
            width: { label: "width", units: "px"},
            height: { label: "height", units: "px"},
            meancolor: { label: "color", handler: function(clr) { 
                clrhex = [];  
                for (i in clr) { clrhex.push(Math.round(clr[i]).toString(16)); } 
                return "#" + clrhex.join("");
                }, units: ""}
            };
        
    },
    
    inspection_measurements: function() {
        return SS.inspectionhandlers["feature_measurements"]();
    },
    
    measurement_meancolor: function(result) {
        arr = $.parseJSON(r.string);
        return Math.round((arr[0] + arr[1] + arr[2]) / 3);
    }
};

    
