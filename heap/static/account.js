$(document).ready(function() {
    "use strict";
    $('#apply_changes_button').click(function() {
        var error = false;
        $('#password_error').text('');
        $('#email_error').text('');
        if ($('#password').val() !== $('#password_repeat').val()) {
            $('#password_error').text('Your passwords don\'t seem to match');
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
        if (!error) {
            $.post("/account/", {email:$('#email').val(), password:$('#password').val()}, function(res) {
                if (res.success) {
                    $('#saved').slideDown(200);
                    setTimeout(function() {
                        $('#saved').slideUp(200);
                    }, 1000);
                } else {
                    window.location = res.url;
                }
            });
        }
    });
    $('#email').keypress(function(e) {
      if (e.which === 13) {
        $('#apply_changes_button').click();
      }
    });

    $('#password').keypress(function(e) {
      if (e.which === 13) {
        $('#apply_changes_button').click();
      }
    });

    $('#password_repeat').keypress(function(e) {
      if (e.which === 13) {
        $('#apply_changes_button').click();
      }
    });
    $('#sign_out_button').click(function() {
        $.post("/signout/", {}, function(res) {
            window.location = res.url;
        });
    });
});
