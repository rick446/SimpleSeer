var poll = function poll(){
    $.ajax(
        {
        url: "poll",
        success: function(data){
                    console.log("check redis");
                },
        error: function(data){
                    console.log("polling error occured");
                },
        complete: function(data){
                    console.log("polling complete");
                    //~ setInterval(poll, 2000);
                }
        }
    );
}

$(document).ready(
    window.setInterval(poll, 2000)
);

