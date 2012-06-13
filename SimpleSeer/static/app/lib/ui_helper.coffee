Pallette = ->
  $this = this
  @colors =
    candy:
      red: "#BA0000"
      yellow: "#FF8F00"
      orange: "#FF510D"
      purple: "#291628"
      green: "#507A00"

    blues: [ "#012340", "#183E4C", "#3D736D", "#8EBF9F", "#E9F2C9" ]

  @getColor = (position) ->
    $this.colors.blues[position]