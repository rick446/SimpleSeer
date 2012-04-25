!function ($) {

  $(function(){

    // make code pretty
    window.prettyPrint && prettyPrint()


    // add tipsies to grid for scaffolding REMOVE
    if ($('#grid-system').length) {
      $('#grid-system').tooltip({
          selector: '.show-grid > div'
        , title: function () { return $(this).width() + 'px' }
      })
    }

		
    // tooltip demo
    $('section').tooltip({
      selector: "a[rel=tooltip]"
    })

    // popover demo
    $("a[rel=popover]")
      .popover()
      .click(function(e) {
        e.preventDefault()
      })

    // button state
    $('.loading')
      .click(function () {
        var btn = $(this)
        btn.button('loading')
        setTimeout(function () {
          btn.button('reset');
					$('.modal').modal('hide')
        }, 2000)
      })

    // javascript build logic
    var inputsComponent = $("#listed input");

    // toggle all checkboxes
    $('.toggle-all').on('click', function (e) {
      inputsComponent.attr('checked', !inputsComponent.is(':checked'))
    })

    
  })

// Modified from the original jsonpi https://github.com/benvinegar/jquery-jsonpi
$.ajaxTransport('jsonpi', function(opts, originalOptions, jqXHR) {
  var url = opts.url;

  return {
    send: function(_, completeCallback) {
      var name = 'jQuery_iframe_' + jQuery.now()
        , iframe, form

      iframe = $('<iframe>')
        .attr('name', name)
        .appendTo('head')

      form = $('<form>')
        .attr('method', opts.type) // GET or POST
        .attr('action', url)
        .attr('target', name)

      $.each(opts.params, function(k, v) {

        $('<input>')
          .attr('type', 'hidden')
          .attr('name', k)
          .attr('value', typeof v == 'string' ? v : JSON.stringify(v))
          .appendTo(form)
      })

      form.appendTo('body').submit()
    }
  }
})

}(window.jQuery)