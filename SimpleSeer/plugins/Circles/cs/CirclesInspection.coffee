class Circles
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Circle Detection"
plugin this, circles:Circles
