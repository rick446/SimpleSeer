SubView = require '../subview'
application = require '../../application'
template = require './templates/tableView'

module.exports = class tableView extends SubView
  tableData: []
  columnOrder: []
  emptyCell: ""
  template:template

  initialize: =>
    @emptyCell = @options.emptyCell if @options.emptyCell
    @columnOrder = @options.columnOrder if @options.columnOrder
    super()

  empty: =>
    @tableData = []

  addRow: (row) =>
    newRow = {}
    for i,o of row
      if @isEmpty o
        o = @emptyCell
      newRow[i] = o
    @tableData.push newRow

  getType: (val) =>
    """
    56%
    percent = if ends with %
    int = if is int
    date = if typeof date (if !moment, switch to moment)
    """

  isEmpty: (val) =>
    val == false || val == ''

  afterRender: =>
    l = @$el.find('thead :visible th')
    for dn in l
      if dn.innerHTML == "Capture Time"
        dn.innerHTML += " " + new Date().toString().match(/\(.*\)/g)
    @$el.find('.tablesorter').tablesorter({widgets: ['zebra']})

  getRenderData: =>
    retHeader = []
    retRow = []
    rr = []
    
    #populate initial coloumn order
    for col in @columnOrder
      retHeader.push col
      
    #populate row data
    for row in @tableData
      _r = []
      while _r.length < retHeader.length
        _r.push @emptyCell
      for col, rowItem of row
        i = retHeader.indexOf(col)
        if i == -1
          retHeader.push col
          i = retHeader.indexOf(col)
        _r[i] = rowItem
      rr.push _r
      
    #fill each row with empty cells if needed
    for a in rr
      while a.length < retHeader.length
        a.push @emptyCell
      retRow.push a

    csvString = ''
    
    for csvheader in retHeader
      csvString += '"'+csvheader+'",'
    csvString = $("<div/>").html(csvString.slice(0,-1)).text()
    csvString += "\n"
      
    for csvrow in retRow
      for item in csvrow
        if item == '---'
          item = ''
        csvString += '"'+item+'",'
      csvString = csvString.slice(0,-1)
      csvString += "\n"
    #@exportUrl = @options.parent.filtercollection.getUrl(true, {headers:retHeader})
    #console.log @exportUrl
    #@$el.find('#csvlink').attr('href','/downloadFrames/csv')
    uriContent = "data:text/csv," + encodeURIComponent(csvString)
    exportUrl = uriContent
    #console.log @$el.find('#csvlink').attr('href')
    #@$el.find('#excellink').attr('href','/downloadFrames/excel'+@exportUrl)
    return {header:retHeader,row:retRow,exportUrl:exportUrl}
