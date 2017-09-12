$(document).ready(function() {
    "use strict";
    $('#sign_up_button').click(function(){
        var error = false;
        $('#password_error').text('');
        $('#email_error').text('');
        if ($('#password').val() !== $('#password_repeat').val()){
            $('#password_error').text('Your passwords don\'t seem to match.');
            error = true;
        }
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
            $.post("/signup/",{email:$('#email').val(), password:$('#password').val()}, function(res) {
                if (res.error) {
                    $('#email_error').text('This email is already being used');
                    return;
                }
                window.location = res.url;
            });
        }
    });
    $('input').keypress(function(e) {
      if (e.which === 13) {
        $('#sign_up_button').click();
      }
    });
});
