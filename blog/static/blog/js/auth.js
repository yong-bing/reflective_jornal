$(document).ready(function () {
    // 登录相关代码
    // 检查本地存储中是否有保存的用户名
    let savedUsername = localStorage.getItem('rememberedUsername');
    if (savedUsername) {
        $('#username').val(savedUsername);
        $('#password').focus();
        $('#rememberMe').prop('checked', true);
    }

    // 点击验证码图片刷新
    $('#captcha-image').on('click', refreshCaptcha);

    $('#loginForm').on('submit', function (e) {
        e.preventDefault();
        let formData = new FormData(this);

        $.ajax({
            url: '/login/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').val()
            },
            success: function (response) {
                console.log(response);
                if (response.success) {
                    // 登录成功
                    if ($('#rememberMe').is(':checked')) {
                        localStorage.setItem('authToken', response.token);
                        localStorage.setItem('rememberedUsername', response.username);
                    } else {
                        localStorage.removeItem('authToken');
                        localStorage.removeItem('rememberedUsername');
                    }
                    window.location.href = '/';
                } else {
                    // 登录失败
                    // 清除所有错误信息
                    $('.error-message').html('');
                    $('.form-control').removeClass('is-invalid is-valid');

                    // 显示新的错误信息
                    $.each(response.errors, function (key, value) {
                        if (key === 'captcha') {
                            $('#id_captcha-error').html(value);
                            $('#id_captcha').addClass('is-invalid');
                        } else {
                            $(`#id_password-error`).html(value);
                            $(`#id_${key}`).addClass('is-invalid');
                        }
                    });

                    refreshCaptcha();
                }
            }
        });
    });

    // 注册相关代码
    // 密码一致性检查
    $('#id_confirm_password').on('input', function () {
        let password = $('#id_password').val();
        let confirmPassword = $(this).val();
        if (password === confirmPassword) {
            $('#id_confirm_password-error').html('');
            $('#id_confirm_password').removeClass('is-invalid').addClass('is-valid');
            $('#id_password').removeClass('is-invalid').addClass('is-valid');
        } else {
            $('#id_confirm_password-error').html('两次输入的密码不一致');
            $('#id_confirm_password').removeClass('is-valid').addClass('is-invalid');
            $('#id_password').removeClass('is-valid').addClass('is-invalid');
        }
    });

    $('#registerForm').on('submit', function (e) {
        e.preventDefault();
        let formData = new FormData(this);

        $.ajax({
            url: '/register/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').val()
            },
            success: function (response) {
                if (response.success) {
                    alert('注册成功！请登录');
                    window.location.href = '/login/';
                } else {
                    // 清除所有错误信息
                    $('.error-message').html('');
                    $('.form-control').removeClass('is-invalid is-valid');

                    // 显示新的错误信息
                    $.each(response.errors, function (key, value) {

                        if (key === '__all__') {
                            $('#id_confirm_password-error').html(value);
                            $('#id_confirm_password').addClass('is-invalid');
                            $('#id_password').addClass('is-invalid');
                        } else {
                            $(`#id_${key}-error`).html(value);
                            $(`#id_${key}`).addClass('is-invalid');
                        }
                    });
                    refreshCaptcha();
                }
            }
        });
    });


    // 重置密码相关代码
    $('#resetForm').on('submit', function (e) {
        e.preventDefault();
        let formData = new FormData(this);

        $.ajax({
            url: '/reset_password/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').val()
            },
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                    window.location.href = '/login/';
                } else {
                    $('.error-message').html('');
                    $('.form-control').removeClass('is-invalid is-valid');
                    refreshCaptcha();

                    $.each(response.errors, function (key, value) {
                        $(`#${key}-error`).html(value);
                        $(`#${key}`).addClass('is-invalid');
                    });
                }
            }
        });
    });

    $('#confirmResetForm').on('submit', function (e) {
        e.preventDefault();
        let formData = new FormData(this);

        $.ajax({
            url: window.location.href,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': $('[name="csrfmiddlewaretoken"]').val()
            },
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                    window.location.href = '/login/';
                } else {
                    alert(response.errors);
                }
            }
        });
    });

    // 共用的刷新验证码函数
    function refreshCaptcha() {
        $('#captcha-image').attr('src', '/get_captcha?' + new Date().getTime());
    }
});