$(document).ready(function() {
    $('.info').bind('click', function() {
        $(this).parent().parent().parent().find('.detail').toggle();
        $(this).parent().parent().addClass('expand');
        return false;
    });
});