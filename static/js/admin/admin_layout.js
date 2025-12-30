$(document).ready(function () {
    $('#mobileMenuBtn').on('click', function (e) {
        e.stopPropagation();
        $('#mainNav').toggleClass('show');
        const icon = $(this).find('i');
        if (icon.hasClass('fa-bars')) {
            icon.removeClass('fa-bars').addClass('fa-times');
            $(this).css('background', 'rgba(239, 68, 68, 0.8)');
        } else {
            icon.removeClass('fa-times').addClass('fa-bars');
            $(this).css('background', 'rgba(255, 255, 255, 0.1)');
        }
    });

    $('#mainNav a').on('click', function () {
        $('#mainNav').removeClass('show');
        $('#mobileMenuBtn i').removeClass('fa-times').addClass('fa-bars');
        $('#mobileMenuBtn').css('background', 'rgba(255, 255, 255, 0.1)');
    });

    $(document).on('click', function (e) {
        if (!$(e.target).closest('header').length && $('#mainNav').hasClass('show')) {
            $('#mainNav').removeClass('show');
            $('#mobileMenuBtn i').removeClass('fa-times').addClass('fa-bars');
            $('#mobileMenuBtn').css('background', 'rgba(255, 255, 255, 0.1)');
        }
    });

    $('#mainNav').on('click', function (e) {
        e.stopPropagation();
    });

    $.ajax({
        url: '{{ url_for("user.check_login") }}',
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            const userMenu = $('#userMenu');
            const loginLink = $('#loginLink');
            const userName = $('#userName');
            const userDropdown = $('#userDropdown');

            if (data.logged_in) {
                userName.text(data.full_name).css('display', 'block');
                loginLink.css('display', 'none');
                userDropdown.css('display', 'none');
                userMenu.on('mouseenter', function () {
                    userDropdown.css('display', 'block');
                }).on('mouseleave', function () {
                    userDropdown.css('display', 'none');
                });
                userDropdown.find('a').on('click', function () {
                    userDropdown.css('display', 'none');
                });
            } else {
                loginLink.css('display', 'inline');
                userName.css('display', 'none');
                userDropdown.css('display', 'none');
                userMenu.off('mouseenter mouseleave');
                userMenu.on('click', function () {
                    window.location.href = '{{ url_for("auth.login") }}';
                });
            }
        },
        error: function (xhr, status, error) {
            console.error('Lỗi khi kiểm tra đăng nhập:', status, error);
            const userMenu = $('#userMenu');
            const loginLink = $('#loginLink');
            const userName = $('#userName');
            const userDropdown = $('#userDropdown');
            loginLink.css('display', 'inline');
            userName.css('display', 'none');
            userDropdown.css('display', 'none');
            userMenu.off('mouseenter mouseleave');
            userMenu.on('click', function () {
                window.location.href = '{{ url_for("auth.login") }}';
            });
        }
    });

    $('#logoutBtn').on('click', function (e) {
        e.preventDefault();
        $.ajax({
            url: '{{ url_for("auth.logout") }}',
            method: 'POST',
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                    window.location.href = response.redirect;
                }
            },
            error: function (xhr, status, error) {
                console.error('Lỗi khi đăng xuất:', status, error);
                alert('Đã xảy ra lỗi khi đăng xuất.');
            }
        });
    });
});
$(document).ready(function () {
    // Kiểm tra trạng thái đăng nhập
    $.ajax({
        url: '{{ url_for("user.check_login") }}',
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            if (data.logged_in) {
                // Thêm tên người dùng vào header nếu cần
            }
        },
        error: function (xhr, status, error) {
            console.error('Lỗi khi kiểm tra đăng nhập:', status, error);
        }
    });
});