$(document).ready(function() {
    $('.info').bind('click', function() {
        var trig, purl, size, info;
        trig = $(this).attr('title');
        purl = $(this).attr('href');
        size = $(this).attr('rel');
        info = $(this).next('.hidden').html();
        $('.active').removeClass('active');        
        $('.dialog').remove();
        $(this).addClass('active');    
        $(this).append('<div class="dialog '+size+'"><div class="content clearfix"></div></div>').show('fast', function () {
            if (info) {$('.dialog .content').prepend(info);}
            $('.dialog .content').after('<span class="arrw"></span>');
            $('.dialog').prepend('<h1>'+trig+'</h1>');
            $('.dialog').prepend('<div class="close">X</div>');
            $('.close, input[value="Cancel"]').bind('click', function() {
                $('.dialog').remove();
                $('.active').removeClass('active');
                return false;
            });
            $(document).keyup(function(e) {
              if (e.keyCode == 27) { $('.close').click(); }   // esc
            });      
        });
        return false;
        purl.abort();
        $(this).unbind('click');
    });
});