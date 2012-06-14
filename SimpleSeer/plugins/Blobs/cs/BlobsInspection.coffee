class Blobs
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Binary Large Object (BLOB) Detected"
# LHS - The setup ini file inspection name
# RHS - The name of this coffee script class
plugin this, blobs:Blobs
