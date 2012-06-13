class SimpleTemplate
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Template Detection"
plugin this, simpleTemplate:SimpleTemplate
