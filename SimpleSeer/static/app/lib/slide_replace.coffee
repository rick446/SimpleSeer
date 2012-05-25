(( $ )->
  $.fn.slideReplace = (content, direction)->
    if $.trim(this.html()) == '' # if the html is empty, no animate is needed
      this.html content
    else
      $("body").css "overflow-x", "hidden"
      if direction == 'left'
        dir = -1
      else
        dir = 1
      target_pos = this.offset().left
      tmp_holder = $('<div/>').css
        width: this.width()
        height: this.height()
        position: 'absolute'
        top: this.offset().top
        left: target_pos+dir*$(window).width()
      tmp_holder.html(content)
      tmp_holder.insertBefore(this)
      this.animate
        left: target_pos+dir*-1*$(window).width()
      tmp_holder.animate
        left:target_pos
        =>
          this.css({'left': 0}).html content
          tmp_holder.remove()
          $("body").css "overflow-x", "auto"
    return this
)( jQuery )