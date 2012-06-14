class FaceFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/face.png" 
    
  represent: () =>
    "Face Detected at (" + @feature.get("x") + ", " + @feature.get("y") + ")"
    
  tableOk: => true
    
  tableHeader: () =>
    ["Horizontal", "Vertical", "Height", "Width", "Color"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("height"), @feature.get("width"), @feature.get("meancolor")]
    
  render: (pjs) =>
    pjs.stroke 0, 180, 180
    pjs.strokeWeight 3
    pjs.noFill()
    pjs.ellipse( @feature.get('x'),@feature.get('y'), @feature.get('width')*.7,@feature.get('height') )
        
plugin this, FaceFeature:FaceFeature

