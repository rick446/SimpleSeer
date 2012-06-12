class Blob
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Blob Detected Derp!"
plugin this, blob:Blob
