class OCR
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Read Text"
plugin this, ocr:OCR
