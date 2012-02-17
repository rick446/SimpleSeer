SimpleSeer.inspectionhandlers.barcode = {
        rendercontrols: function(insp, div_id) {

        },
        
        generate_name: function(parameters) {
            
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

								var ptsX = new Array();
								var ptsY = new Array();
            
								SS.p.beginShape();
                for (pts in f.points) {
                    pt = f.points[pts];
                    SS.p.vertex(pt[0], pt[1]);
                    ptsX.push(pt[0]);
                    ptsY.push(pt[1]);
                }
                SS.p.endShape(SS.p.CLOSE)
            
                if (!inspection.id || inspection.id == "preview") {
                    continue;
                }
                div_id = "inspection_" + inspection.id + "_feature_"+i.toString();
                
                if ($("#"+div_id).length) {
                    continue;
                }


	
                
								SS.Display.addDisplayObject(div_id, _.min(ptsX), _.min(ptsY), f.width, f.height);
								SS.DisplayObject.addNavZoom(div_id);
								SS.DisplayObject.addNavInfo(div_id,
										"Barcode " + i.toString() + " Properties",
										{
											x: { label: "top", units: "px" },
											y: { label: "left", units: "px"},
											width: { label: "width", units: "px"},
											height: { label: "height", units: "px"},
											angle: { label: "angle", units: "&deg;"},
											area: { label: "area", units: "px"},

										},
											
										inspection,
										i
								);
            }
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

						if(SS.featuresets[insp.id].length > 0 ){
            info.append(
                SS.Watchlist.renderItem({
									label: "Barcode",
									units: "",
									handler: function(arr) {
                    return arr[0].featuredata.data
                    }},
									SS.featuresets[insp.id],
									"Data:",
									insp));
						}
        },

        
        manipulate: function() { 
        },

};
