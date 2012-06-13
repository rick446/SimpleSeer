class SimpleTemplateFeature
  constructor: (feature) ->
    @feature = feature
   
  
  icon: () => "/img/template.png" 
    
  represent: () =>
    "Template Detected at (" + @feature.get("x") + ", " + @feature.get("y") + ") with quality" + @feature.get("featuredata").quality + "."
    
  tableOk: => true
    
  tableHeader: () =>
    ["X Positon", "Y Position", "Quality"]
    
  tableData: () =>
    [@feature.get("x"), @feature.get("y"), @feature.get("featuredata").quality]
    
  render: (pjs) =>
    pjs.stroke 180, 0, 180
    pjs.strokeWeight 3
    pjs.noFill()
    x0 = @feature.get('x')
    y0 = @feature.get('y')
    pjs.rect( x0, y0, @feature.get('width'), @feature.get('height'))

plugin this, TemplateMatch:SimpleTemplateFeature
