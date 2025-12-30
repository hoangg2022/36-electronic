$(document).ready(function () {
    $('#login-btn').click(function () {
        var username = $('#username').val();
        var password = $('#password').val();
        console.log("Sending login request:", { username: username, password: password }); // Debug log
        $.ajax({
            url: '/login',
            type: 'POST',
            data: { username: username, password: password },
            success: function (response) {
                console.log("Received response:", response);
                $('#error-msg').removeClass('success error').hide();
                if (response.success) {
                    $('#error-msg').text(response.message).addClass('success').show();
                    if (response.redirect) {
                        console.log("Redirecting to:", response.redirect);
                        setTimeout(function () {
                            window.location.href = response.redirect;
                        }, 1000);
                    }
                } else {
                    $('#error-msg').text(response.message).addClass('error').show();
                }
            },
            error: function (xhr) {
                console.log("AJAX error:", xhr);
                $('#error-msg').text('Sai tên đăng nhập hoặc mật khẩu: ' + xhr.responseJSON.message).addClass('error').show();
            }
        });
    });

    $('#forgot-link').click(function (e) {
        e.preventDefault();
        window.location.href = '/forgot_password';
    });

    $('#register-link').click(function (e) {
        e.preventDefault();
        window.location.href = '/register';
    });
});