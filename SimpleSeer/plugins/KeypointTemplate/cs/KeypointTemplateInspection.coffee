class KeypointTemplate
  constructor: (inspection) ->
    @inspection = inspection
  represent: () =>
    "Keypoint Template Match"
plugin this, keypointTemplate:KeypointTemplate
