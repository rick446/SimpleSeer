class OCRFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/ocr.png" 
    
  represent: () =>
    "Text Detected in image:" + @feature.get("featuredata").text 
    
  tableOk: => true
    
  tableHeader: () =>
    ["X Positon", "Y Position", "Text"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("featuredata").text]
    
  render: (pjs) =>
    pjs.stroke 0, 180, 180
    pjs.strokeWeight 6
    pjs.noFill()
    pjs.rect(0,0, @feature.get('width')-3, @feature.get('height')-3  )
plugin this, OCRFeature:OCRFeature
