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


	
                
								SS.Display.addDisplayObject(div_id, Math.min(ptsX), Math.max(ptsY), f.width, f.height);
								//SS.DisplayObject.addNavZoom(div_id);
								//~ SS.DisplayObject.addNavInfo(div_id,
										//~ "Barcode " + i.toString() + " Properties",
										//~ {
											//~ x: { label: "top", units: "px" },
											//~ y: { label: "left", units: "px"},
											//~ width: { label: "width", units: "px"},
											//~ height: { label: "height", units: "px"},
											//~ angle: { label: "angle", units: "&deg;"},
											//~ area: { label: "area", units: "px"},
										//~ },
										//~ inspection,
										//~ i
								//~ );
								//~ SS.DisplayObject.addNavItem(div_id, "gear", "Edit this Inspection", function (e) {
												//~ disp_object_id = $(e.target).parent().parent().parent().attr("id");
												//~ id = disp_object_id.split("_")[1];
												//~ feature_index = disp_object_id.split("_")[3];
												//~ index = SS.Inspection.getIndex(id);
												//~ insp = SS.inspections[index];
												//~ feat = SS.featuresets[id][feature_index];
												//~ SS.mouseBlock = false;             
												//~ SS.action.task = "barcode";
												//~ SS.action.update = id;
												//~ 
												//~ insp.norender = true;
								//~ });
								//~ 
                
            }


        },
        

        
        manipulate: function() { 
        },

};
