class BarcodesFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/barcode.png" 
    
  represent: () =>
    "Barcode detected in image at : (" + @feature("x") + "," + @feature("y") "), with data <" + @feature.get("featuredata").data + ">."
    
  tableOk: => true
    
  tableHeader: () =>
    ["X Positon", "Y Position","Width", "Height", "Data"]
    
  tableData: () =>
    [@feature.get("x"),
     @feature.get("y"),
     @feature.get("width"),
     @feature.get("height"),
     @feature.get("featuredata").data]
    
  render: (pjs) =>
    pjs.stroke 153,0,76
    pjs.strokeWeight 3
    pjs.noFill()
    pjs.rect(@feature.get('x'),@feature.get('y'), @feature.get('width'), @feature.get('height') )
plugin this, Barcode:BarcodesFeature
