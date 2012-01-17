$.expr[':']['nth-of-type'] = function(elem, i, match) {
    if (match[3].indexOf("n") === -1) return i + 1 == match[3];
    var parts = match[3].split("+");
    return (i + 1 - (parts[1] || 0)) % parseInt(parts[0], 10) === 0;
};
$(document).ready(function() {
    var howh = $(document).height();
    $('body').css('height',+howh+'px');
    $('.c3 article:nth-of-type(3n), .c4 article:nth-of-type(4n), .c4 .col:nth-of-type(4n), .c3 .col:nth-of-type(3n), .c2c .col:eq(1),  .c2c .col:eq(3)').css('margin-right','0'); /* because ie is poorly done - this clips the last div */
    $('.c2c .c2').css('background','transparent');
    $('.peek').click(function(e){    /* shows the filter bar */
        $(this).next('.hidden').toggleClass('hidden');
        e.preventDefault();
    });
    $('.object').hover(function(){    /* shows the object nav bar */
        $(this).find('.hidden').removeClass('hidden');
    },
    function(){
        $(this).find('nav').addClass('hidden');
    });
