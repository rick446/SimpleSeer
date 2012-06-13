class CircleFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/circle.png" 
    
  represent: () =>
    "Circle Detected at (" + @feature.get("x") + ", " + @feature.get("y") + ") with radius " + @feature.get("featuredata").r
    
  tableOk: => true
    
  tableHeader: () =>
    ["X Positon", "Y Position", "Radius"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("featuredata").r]
    
  render: (pjs) =>
    pjs.stroke 0, 180, 180
    pjs.strokeWeight 3
    pjs.noFill()
    pjs.ellipse( @feature.get('x'), @feature.get('y'), @feature.get('featuredata').r*2, @feature.get('featuredata').r*2 )
plugin this, Circle:CircleFeature
