
/*$( document ).ajaxStart( function() {
    $( '#spinner' ).show();
}).ajaxStop( function() {
    $( '#spinner' ).hide();
});
*/
/* Get the service status of the user */
$(function() {
    var img_check = ' <img src="/static/check.png" alt="OK" />';
    var img_error = ' <img src="/static/exclamation_mark.png" alt="ERROR" />';

    $.getJSON("/userstatus/client/?format=json", function(data) {
        var image = '';
        if(data.active) {
            image = img_check;
        } else {
            image = img_error;
        }
        $("#client_status").html(image);
    });
    $.getJSON('/userstatus/wireless/?format=json', function(data) {
        var image = '';
        if(data.active) {
            image = img_check;
        } else {
            image = img_error;
        }
        $("#wireless_status").html(image);
    });

});
