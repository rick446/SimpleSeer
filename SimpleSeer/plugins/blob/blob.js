SimpleSeer.inspectionhandlers.blob = {
        rendercontrols: function(insp, div_id) {

            onchange = function(e, ui) {
                params = { 
                    threshval: $("#"+insp.id+"_threshval").slider("value"),
                    invert: $("#"+insp.id+"_invert").is(":checked")
                };
                SS.Inspection.preview("blob", params);
            };
            
            
            onapply = function() {
                insp.norender = false;
                params = { 
                    threshval: $("#"+insp.id+"_threshval").slider("value"),
                    invert: $("#"+insp.id+"_invert").is(":checked")
                };
                
                if (insp.id == "preview") {
                    SS.Inspection.add(insp.method, params);
                } else {
                    insp.parameters = params;
                    SS.Inspection.update(insp);
                }
                
                $("#" + div_id).fadeOut(500).remove();
                SS.resetAction(); 
                
            }
            
            oncancel = function() {
                insp.norender = false;
                SS.Inspection.cancelPreview();
                $("#" + div_id).fadeOut(500).remove();
                SS.resetAction();   
                SS.Frame.refresh();
            };
            
            var defaults = {threshval: 127, invert: false};
            if (insp.id != "preview") {
                defaults["threshval"] = insp.parameters.threshval;
                defaults["invert"] = insp.parameters.invert;
            } 
            
            
            
            $("#" + div_id).append($("<h2/>").append("Object Detection"));
            //TODO make this an editable text field for "name"

    
            $("#" + div_id).append(
                $("<h3/>").append("Color")
            ).append(
                SS.InspectionControl.checkbox(insp.id + "_invert", "invert", "Find Dark Blobs", defaults.invert, onchange) 
            ).append(
                $("<h3/>").append("Threshold")
            ).append(
                SS.InspectionControl.slider(insp.id + "_threshval", "threshval", "", defaults.threshval, 0, 255, 1, onchange)
            ).append(
                SS.InspectionControl.applyCancelButton(insp, onapply, oncancel)
            );
        },
        dashboard: function(insp) {
            dash_id = "dash_" + insp.id;
            
            div = $("#" + dash_id + " > .dashobject-nav");
            
            div.append($("<nav/>").append(
                SS.navItem("Remove Object Detection", "close", function(e) {
                    SS.Inspection.remove(insp);
                    SS.mouseBlock = false;
                    $(".tooltip").remove();
                    return false;

                })
            ));
            
            
            info = $("<div/>", { class: "info"} );
            div.append(info);
                    
            
            
            
            info.append(
                SS.Watchlist.renderItem({label: "objects", units: "", handler: function(arr) {
                    return arr.length
                    }}, SS.featuresets[insp.id], "count", insp)
            /*).append(
                SS.Watchlist.renderItem({label: "topmost", units: "px"}, SS.Feature.min(insp.id, "y").y, "y", insp, { max: "y" })
            ).append(
                SS.Watchlist.renderItem({label: "leftmost", units: "px"}, insp.parameters.w, "width", insp)
            ).append(
                SS.Watchlist.renderItem({label: "bottommost", units: "px"}, insp.parameters.h, "height", insp)
            ).append(
                SS.Watchlist.renderItem({label: "rightmost", units: "px"}, insp.parameters.h, "height", insp)
            ).append(
                SS.Watchlist.renderItem({label: "color", units: "", handler: function(clr) { 
                    clrhex = [];  
                    for (i in clr) { clrhex.push(Math.round(clr[i]).toString(16)); } 
                    return "#" + clrhex.join("");
                    }}, SS.featuresets[insp.id][0].meancolor, "meancolor", insp, { index: 0 })
            */);
            
                  
        },
        generate_name: function(parameters) {
            if (parameters.invert) {
                return "Dark Objects";    
            } else {
                return "Light Objects";
            }
            
        },
        
        summary: function(insp) {
            if (SS.featuresets && insp.id in SS.featuresets) {
              return SS.featuresets[insp.id].length.toString() + " found";
            } else {
               return "none found";
            }
        },
        
        hover: function() {
                
            
            
        },
        
        render: function () {

            
        },
        render_features: function (features, inspection) {
            if (features.length == 0) {
                return;
            }
            
            if (inspection.norender) {
                return;
            }
            
            SS.p.stroke(0);
            for (i in features) {
                f = features[i];
                clr = f.meancolor;
                for (index in clr) {
                    clr[index] = Math.round(clr[index]);
                }

                if (inspection.id != SS.action.highlight) {
                    SS.p.stroke(0, 180, 180);
                    SS.p.fill(0, 128, 128, 60);

                } else {
                    SS.p.stroke(0, 255, 255);
                    SS.p.fill(0, 180, 180, 75);


                }
            
                SS.p.beginShape();
                for (c in f.featuredata.mContour) {
                    pt = f.featuredata.mContour[c];
                    SS.p.vertex(pt[0], pt[1]);
                }
                pt = f.featuredata.mContour[0];
                SS.p.vertex(pt[0], pt[1]);
                SS.p.endShape();
            
                if (!inspection.id || inspection.id == "preview") {
                    continue;
                }
                div_id = "inspection_" + inspection.id + "_feature_"+i.toString();
                
                if ($("#"+div_id).length) {
                    continue;
                }
                
                SS.Display.addDisplayObject(div_id, f.points[0][0], f.points[0][1], f.width, f.height);
                SS.DisplayObject.addNavZoom(div_id);
                SS.DisplayObject.addNavInfo(div_id, "Blob " + i.toString() + " Properties", {
                    x: { label: "top", units: "px" },
                    y: { label: "left", units: "px"},
                    width: { label: "width", units: "px"},
                    height: { label: "height", units: "px"},
                    angle: { label: "angle", units: "&deg;"},
                    area: { label: "area", units: "px"},
                    meancolor: { label: "color", handler: function(clr) { 
                        clrhex = [];  
                        for (i in clr) { clrhex.push(Math.round(clr[i]).toString(16)); } 
                        return "#" + clrhex.join("");
                        }, units: ""}
                }, inspection, i);
                SS.DisplayObject.addNavItem(div_id, "gear", "Edit this Inspection", function (e) {
                        disp_object_id = $(e.target).parent().parent().parent().attr("id");
                        id = disp_object_id.split("_")[1];
                        feature_index = disp_object_id.split("_")[3];
                        index = SS.Inspection.getIndex(id);
                        insp = SS.inspections[index];
                        feat = SS.featuresets[id][feature_index];
                        SS.mouseBlock = false;             
                        SS.action.task = "blob";
                        SS.action.update = id;
                        
                        insp.norender = true;
                });
            }
            
        },
        

        
        manipulate: function() { 
            startx = SS.action['startpx'][0];
            starty = SS.action['startpx'][1];
            insp = '';
            if (!SS.action.update) {
                insp = { id: "preview", method: "blob", parameters: {threshval: 127 }};
                SS.Inspection.control(insp, startx, starty);
            } else {
                insp = SS.Inspection.fromId(id);
                SS.Inspection.control(insp, startx, starty);
            }
            
            
            if (isEmpty(SS.preview_data)) {
                console.log("launch_preview");
                SS.Inspection.preview("blob", insp.parameters);            
            }
        },

};
