
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
            image = img_check + ' title="Du har en bruker til foreningsmaskinene. \nSiste vellykkede pålogging: ' + data.last_successful_auth + '" />';
        } else {
            image = img_error + ' title="Ingen konto (mangler Kerberos principal)." />';
        }
        $("#client_status").html(image);
    });
    $.getJSON('/userstatus/wireless/?format=json', function(data) {
        if(data.active) {
            image = img_check + ' title="Du har tilgang til trådløst nettverk. \nSiste vellykkede pålogging: ' + data.last_successful_auth + '" />';
        } else {
            image = img_error + ' title="Ingen trådløskonto (i Radius)." />';
        }
        $("#wireless_status").html(image);
    });

});
