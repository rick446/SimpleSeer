
/* cribbed from http://jsfiddle.net/gaby/3YLQf/ */
$(function(){

    var stretcher = $('#maindisplay > img'),
        element = stretcher[0],
        currentSize = { width: 0, height: 0 },
        $document = $(document);

    $(window).resize(function () {
        stretcher.width(1).height('auto');
        var w = $document.width();
        var h = $document.height();

        if (currentSize.width != w || currentSize.height != h) {
            stretcher.width(w).height('auto');
            if (h < element.height) {
                stretcher.width('auto').height(h);
            }
            currentSize.width = element.width;
            currentSize.height = element.height;
        }
    })

    $(window).load(function () {
        $(this).trigger('resize');
    });

});
