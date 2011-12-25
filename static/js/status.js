$(function() {
    /* Display the service status of the user */
    var img_check = ' <img src="/static/check.png" alt="OK" />';
    var img_error = ' <img src="/static/exclamation_mark.png" alt="ERROR" />';
    var image = '';
    var title = '';

    $.getJSON("/userstatus/client/?format=json", function(data) {
        if(data.active) {
            image = img_check;
            title = "Du har en bruker til foreningsmaskinene. \nSiste vellykkede pålogging: " + data.last_successful_auth;
        } else {
            image = img_error;
            title = "Ingen konto (mangler Kerberos principal).";
        }
        $("#client_status").append(image).prop('title', title).qtip();
    });
    $.getJSON('/userstatus/wireless/?format=json', function(data) {
        if(data.active) {
            image = img_check;
            title = 'Du har tilgang til trådløst nettverk. \nSiste vellykkede pålogging: ' + data.last_successful_auth;
        } else {
            image = img_error;
            title = 'Ingen trådløskonto (i Radius).';
        }
        $("#wireless_status").append(image).prop('title', title).qtip();
    });
    /* Any element with a title attribute gets a pretty qtip */
    $("[title]").qtip();
});
