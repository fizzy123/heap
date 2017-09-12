$(document).ready(function() {
    "use strict";
    $('#sign_in_button').click(function(){
        var error = false;
        $('#email_error').text('');
        $('#password_error').text('');
        if (!validateEmail($('#email').val())) {
            $('#email_error').text('You have not entered a valid email');
            error = true;
        }
        if (!$('#email').val()) {
            $('#email_error').text('Please enter an email address');
            error = true;
        }
        if (!$('#password').val()) {
            $('#password_error').text('Please enter a password');
            error = true;
        }

        if (!error) {
            $.post("/signin/",{email:$('#email').val(), password:$('#password').val()}, function(res) {
                if (res.error) {
                    $('#email_error').text('We don\'t have an account that matches this email and password');
                    return;
                }
                window.location = res.url;
            });
        }
    });
    $('input').keypress(function(e) {
      if (e.which === 13) {
        $('#sign_in_button').click();
      }
    });
});
