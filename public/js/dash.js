$(document).ready(function() {
    $('.options').bind('click', function() {
        alert("hi");
        var trig, purl;
        trig = $(this).attr('title');
        purl = $(this).attr('href');
        $('.active').removeClass('active');
        $('.dash, .dialog').remove();
        $(this).addClass('active');
        $(this).parent().before('<div class="dash"><div class="content clearfix"></div></div>').show( function () {
            $('.dash .content').load(purl + ' .maincontent', function() {
                $.ajax({ url: '/js/modernizr2.js', dataType: 'script', cache: true});
            });
            $('.dash').prepend('<h1>'+trig+'</h1>');
            $('.dash').prepend('<div class="close">X</div>');
            $('.close, input[value="Cancel"]').bind('click', function() {
                $('.dash').remove();
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
    $('nav').draggable();
});
