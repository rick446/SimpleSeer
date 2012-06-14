class Barcodes
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Read Barcode"
plugin this, barcodes:Barcodes
