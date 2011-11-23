
/*$( document ).ajaxStart( function() {
    $( '#spinner' ).show();
}).ajaxStop( function() {
    $( '#spinner' ).hide();
});
*/
/* Get the service status of the user */
$(function() {
    var img_check = ' <img src="/static/check.png" alt="OK"';
    var img_error = ' <img src="/static/exclamation_mark.png" alt="ERROR"';
    var image = '';

    $.getJSON("/userstatus/client/?format=json", function(data) {
        if(data.active) {
            image = img_check + ' title="Account present.\nLast successful authentication: ' + data.last_successful_auth + '" />';
        } else {
            image = img_error + ' title="No client account (kerberos principal)." />';
        }
        $("#client_status").html(image);
    });
    $.getJSON('/userstatus/wireless/?format=json', function(data) {
        if(data.active) {
            image = img_check + ' title="Account present.\nLast successful authentication: ' + data.last_successful_auth + '" />';
        } else {
            image = img_error + ' title="No wireless account." />';
        }
        $("#wireless_status").html(image);
    });

});
