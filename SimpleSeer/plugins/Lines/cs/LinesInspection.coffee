class Lines
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Lines Detection"
plugin this, lines:Lines

