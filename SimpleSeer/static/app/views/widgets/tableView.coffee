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

  isEmpty: (val) =>
    val == false || val == ''

  afterRender: =>
    @$el.find('.tablesorter').tablesorter()

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
    return {header:retHeader,row:retRow}
