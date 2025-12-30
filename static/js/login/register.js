$(document).ready(function () {
    $('#register-btn').click(function () {
        var username = $('#username').val().trim();
        var email = $('#email').val().trim();
        var password = $('#password').val().trim();
        var full_name = $('#full_name').val().trim();
        var birth_date = $('#birth_date').val().trim();

        // Email validation regex
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        // Password validation: at least 8 characters, with uppercase, lowercase, and number
        var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;

        // Clear previous error messages
        $('#register-error-msg').removeClass('success error').hide();

        // Validate required fields
        if (!username) {
            $('#register-error-msg').text('Vui lòng nhập tên đăng nhập').addClass('error').show();
            return;
        }
        if (!email) {
            $('#register-error-msg').text('Vui lòng nhập email').addClass('error').show();
            return;
        }
        // Validate password
        if (!password) {
            $('#register-error-msg').text('Vui lòng nhập mật khẩu').addClass('error').show();
            return;
        }

        if (!full_name) {
            $('#register-error-msg').text('Vui lòng nhập họ và tên').addClass('error').show();
            return;
        }

        if (!birth_date) {
            $('#register-error-msg').text('Vui lòng nhập ngày sinh').addClass('error').show();
            return;
        }



        if (!emailRegex.test(email)) {
            $('#register-error-msg').text('Email không đúng định dạng').addClass('error').show();
            return;
        }



        if (!passwordRegex.test(password)) {
            $('#register-error-msg').text('Mật khẩu phải có ít nhất 8 ký tự bao gồm chữ hoa, chữ thường và số').addClass('error').show();
            return;
        }

        $.ajax({
            url: '/register',
            type: 'POST',
            data: { username: username, email: email, password: password, full_name: full_name, birth_date: birth_date },
            success: function (response) {
                if (response.success) {
                    $('#register-error-msg').text(response.message).addClass('success').show();
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    }
                } else {
                    $('#register-error-msg').text(response.message).addClass('error').show();
                }
            },
            error: function (xhr) {
                $('#register-error-msg').text('Tên đăng nhập hoặc email đã tồn tại').addClass('error').show();
            }
        });
    });

    $('#login-link').click(function (e) {
        e.preventDefault();
        window.location.href = '/login';
    });
});