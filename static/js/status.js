
/*$( document ).ajaxStart( function() {
    $( '#spinner' ).show();
}).ajaxStop( function() {
    $( '#spinner' ).hide();
});
*/
/* Get the service status of the user */
$(function() {
    var img_check = ' <img src="/static/check.png" alt="OK" />';

    $.getJSON("http://localhost:8000/userstatus/client/?format=json", function(data) {
        if(data.active) {
            $("#client_status").html(img_check);
        }
    });
    $.getJSON('http://localhost:8000/userstatus/wireless/?format=json', function(data) {
        if(data.active) {
            $("#wireless_status").html(img_check);
        }
    });

});
