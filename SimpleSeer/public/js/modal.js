$(document).ready(function() {
    $('.trig').bind('click', function() {
        var trig = $(this).attr('title');
        var purl = $(this).attr('href');
        var info = $(this).next('.hidden').html();       
        var howh = $(document).height();
        $('.splash').css('height',+howh+'px');	
        $("html, body").animate({ scrollTop: 0 }, "fast");
        $('.modal, .splash').remove();
        $('body').prepend('<span class="splash"></span>');
        $('body').prepend('<div class="modal"><div class="content clearfix"></div></div>').show('fast', function () {
            if (info) {$('.content').prepend(info);}
            else {
                $('.modal .content').load(purl + ' .maincontent', function() {
                    $.ajax({ url: '/js/modernizr2.js', dataType: 'script', cache: true});
                    $('input[value="Cancel"]').bind('click', function() {
                        $('.modal, .splash').remove();
                        return false;
                    });
                });
            }
            $('.modal').prepend('<h1>'+trig+'</h1>');
            $('.modal').prepend('<div class="close">X</div>');
            $('.close, .splash, input[value="Cancel"]').bind('click', function() {
                $('.modal, .splash').remove();
                return false;
            });    
        });
        return false;
        purl.abort();
        $(this).unbind('click');
    });
    $(document).keyup(function(e) {
      if (e.keyCode == 27) { 
          $('.close').click();
       }
    });    
    $('#message .close').bind('click', function() {
        $(this).parent().remove();
        return false;
    });    
});