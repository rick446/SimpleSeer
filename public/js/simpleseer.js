
/* Make sure the display is always relevant to the browser size
 * parts cribbed from http://jsfiddle.net/gaby/3YLQf/ */

SS = SimpleSeer = new Object();

//initalize the display and the resize function
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
        $('#display').height = stretcher.height();
        $('#display').width = stretcher.width();
        SS.p.size(stretcher.width(), stretcher.height());
        SS.xscalefactor = stretcher.width() /  SS.framedata[0].width
        SS.yscalefactor = stretcher.height() / SS.framedata[0].height
    })

    $(window).load(function () {
        $(this).trigger('resize');
    });

});

//function to retrieve data from webdis
SimpleSeer.getValue = function(key) {
    returndata = $.parseJSON(
        $.ajax({ url: "/GET/" + key + ".json", 
                async: false, 
                dataType: 'json'
            }).responseText
    );
    return returndata['GET'];
};

//import some context from webdis
SimpleSeer.cameras = SimpleSeer.getValue('cameras');
SimpleSeer.framecount = SimpleSeer.getValue('framecount');
SimpleSeer.framedata = [$.parseJSON(SimpleSeer.getValue('currentframedata_0'))];
SimpleSeer.poll_interval = parseFloat(SimpleSeer.getValue('poll_interval'));

/* //check the frame id, if it increments, reload context
setInterval(function(){
   thisframe = SimpleSeer.getValue('framecount');
   if (SimpleSeer.framecount != thisframe) {
       d = new Date();
       $('#maindisplay > img').attr("src", "/GET/currentframe_0.jpg?" + d.getTime());
   }
   SimpleSeer.framecount = thisframe;

}, SimpleSeer.poll_interval * 1000);
 */


SS.p = new Processing('display');
//coloquially, we'll probably always refer to this as SS.p

//this is the "main" loop of the processing app

SS.p.setup = function() {
  SS.p.size($('#maindisplay > img').width(), $('#maindisplay > img').height());
}

SS.setscale = function() {
  SS.p.scale(SS.xscalefactor, SS.yscalefactor)
  SS.mouseX = SS.p.mouseX / SS.xscalefactor;
  SS.mouseY = SS.p.mouseY / SS.yscalefactor;
}


SS.p.draw = function() {
  SS.setscale();
  
  SS.p.background(0, 0);   
  //SS.p.fill(255, 80);  
  //SS.p.rect(SS.mouseX, SS.mouseY, 20, 20);  
 }

 
SS.p.mousePressed = function() {
  //SS.setscale();
  SS.action = { startpx: [SS.mouseX, SS.mouseY] };
   
   
  $("#radial").radmenu("show").css( { zIndex: 99, top: SS.p.mouseY.toString() + "px", left: SS.p.mouseX.toString() + "px" } );
}

//this executes at document.ready
SimpleSeer.setup = function(){
    SS.p.setup();
    SS.p.loop();
    
    $("#radial").radmenu({
        listClass: 'radial_items', // the list class to look within for items
        itemClass: 'radial_item', // the items - NOTE: the HTML inside the item is copied into the menu item
        radius: 100, // radius in pixels
        animSpeed:400, // animation speed in millis
        centerX: 30, // the center x axis offset
        centerY: 100, // the center y axis offset
        selectEvent: "click", // the select event (click)
        onSelect: function($selected){ // show what is returned 
            alert("you clicked on .. " + $selected.index());
            $("#radial").radmenu("hide").css( { zIndex: -1, top: "0px", left: "0px" } );

        },
        angleOffset: 0 // in degrees
    });
}
