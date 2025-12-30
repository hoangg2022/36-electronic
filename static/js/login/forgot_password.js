$(document).ready(function () {
    $('#reset-btn').click(function () {
        var username = $('#username').val();
        var email = $('#email').val();
        var full_name = $('#full_name').val();
        var birth_date = $('#birth_date').val();
        console.log("Sending forgot password request:", { username, email, full_name, birth_date }); // Debug log
        $.ajax({
            url: '/forgot_password',
            type: 'POST',
            data: { username: username, email: email, full_name: full_name, birth_date: birth_date },
            success: function (response) {
                console.log("Received response:", response); // Debug log
                $('#forgot-error-msg').removeClass('success error').hide();
                if (response.success) {
                    $('#forgot-error-msg').text(response.message).addClass('success').show();
                    if (response.redirect) {
                        console.log("Redirecting to:", response.redirect); // Debug log
                        setTimeout(function () {
                            window.location.href = response.redirect;
                        }, 1000);
                    }
                } else {
                    $('#forgot-error-msg').text(response.message).addClass('error').show();
                }
            },
            error: function (xhr) {
                console.log("AJAX error:", xhr); // Debug log
                $('#forgot-error-msg').text('Người dùng không tồn tại').addClass('error').show();
            }
        });
    });

    $('#login-link').click(function (e) {
        e.preventDefault();
        window.location.href = '/login';
    });
});