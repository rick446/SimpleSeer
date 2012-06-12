class BarcodesFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/barcode.png" 
    
  represent: () =>
        "Barcode detected in image at : (" +
        @feature.get("x") +
        "," +
        @feature.get("y") +
        "), with data <" +
        @feature.get("featuredata").data +
        ">."
    
  tableOk: => true
    
  tableHeader: () =>
   [ "X Positon", "Y Position","Width", "Height", "Data"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("width"), @feature.get("height"),  @feature.get("featuredata").data]
    
  render: (pjs) =>
    pjs.stroke 76,0,153
    pjs.strokeWeight 3
    pjs.noFill()
    x0 = @feature.get('x')-(@feature.get('width')/2)
    y0 = @feature.get('y')-(@feature.get('height')/2)
    pjs.rect(x0,y0, @feature.get('width'), @feature.get('height') )
plugin this, Barcode:BarcodesFeature
