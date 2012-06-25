module.exports = charts =
  #highcharts
  area : require './highcharts/HCArea'
  areaspline : require './highcharts/HCAreaspline'
  bar : require './highcharts/HCBar'
  column : require './highcharts/HCColumn'
  line : require './highcharts/HCLine'
  pie : require './highcharts/HCPie'
  scatter : require './highcharts/HCScatter'
  spline : require './highcharts/HCSpline'

  #custom
  marbleoverview : require './custom/Marbleoverview'
  sumbucket : require './custom/Sumbucket'
  total : require './custom/Total'
