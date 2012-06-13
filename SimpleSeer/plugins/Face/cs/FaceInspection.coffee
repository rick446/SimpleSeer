class Face
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Face Detection"
plugin this, face:Face
