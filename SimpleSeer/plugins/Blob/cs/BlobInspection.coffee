class Blob
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Blob Detected Derp!"
# LHS - The setup ini file inspection name
# RHS - The name of this coffee script class
plugin this, blob:Blob
