
/* Make sure the display is always relevant to the browser size
 * parts cribbed from http://jsfiddle.net/gaby/3YLQf/ */
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


SimpleSeer = new Object();
SimpleSeer.getValue = function(key) {
    returndata = $.parseJSON(
        $.ajax(
            {
                url: "/GET/" + key + ".json", 
                async: false, 
                dataType: 'json'
            }
        ).responseText
    );
    
    return returndata['GET'];
};

SimpleSeer.cameras = SimpleSeer.getValue('cameras');
SimpleSeer.framecount = SimpleSeer.getValue('framecount');
SimpleSeer.poll_interval = parseFloat(SimpleSeer.getValue('poll_interval'));


setInterval(function(){
   thisframe = SimpleSeer.getValue('framecount');
   if (SimpleSeer.framecount != thisframe) {
       d = new Date();
       $('#maindisplay > img').attr("src", "/GET/currentframe_0.jpg?" + d.getTime());
   }
   SimpleSeer.framecount = thisframe;

}, SimpleSeer.poll_interval * 1000);
