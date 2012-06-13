class KeypointTemplateFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/template.png" 
    
  represent: () =>
    "Keypoint Feature Matched at (" + @feature.get("x") + ", " + @feature.get("y") + ") with size (" + @feature.get("width") + "," + @feature.get("height")+")."
    
  tableOk: => true
    
  tableHeader: () =>
    ["X Positon", "Y Position", "Width","Height"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("width"), @feature.get("height")]
    
  render: (pjs) =>
    pjs.stroke 0, 180, 180
    pjs.strokeWeight 3
    pjs.noFill()
    contour = @feature.get('featuredata').contour
    last = contour[contour.length-1]
    for current in contour
        pjs.line( last[0],last[1],current[0],current[1] )
        last = current
        
plugin this, KeypointMatch:KeypointTemplateFeature
