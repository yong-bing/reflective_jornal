// 点击验证码图片刷新验证码
$('#verification_code_img').click(function () {
    $(this).attr('src', '/get_verification_code?_=' + Math.random());
});

// 提交ajax请求之后刷新验证码
$(document).ajaxComplete(function () {
    $('#verification_code_img').attr('src', '/get_verification_code?_=' + Math.random());
});

// 登陆验证
$('.login_btn').click(function () {
    let username = $('#username').val();
    let password = $('#password').val();
    let verification_code = $('#verification_code').val();
    let csrfmiddlewaretoken = $('[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: '/login/',
        type: 'post',
        data: {
            username: username,
            password: password,
            verification_code: verification_code,
            csrfmiddlewaretoken: csrfmiddlewaretoken
        },
        success: function (data) {
            if (data.username) {
                window.location.href = '/index/';
            } else {
                alert(data.msg);
            }
        }
    });
});

// 注册验证
$('.register_btn').click(function () {
    let user_info = new FormData();
    let request_data = $('form').serialize();
    $.each($('form input[type != "file"]'), function (index, item) {
        user_info.append($(item).attr('name'), $(item).val());
    });
    user_info.append('avatar', $('#id_avatar')[0].files[0]);

    $.ajax({
        url: '/register/',
        type: 'POST',
        data: user_info,
        processData: false,
        contentType: false,
        success: function (data) {
            if (data.username) {
                alert('注册成功');
                window.location.href = '/login/';
            } else {
                $('.error').html('');
                $.each(data.msg, function (key, value) {
                    if (key == "__all__") {
                        $('#id_confirm_password').next().html(value)
                    }
                    $('#id_' + key).next().html(value)
                });
            }
        }
    });
});

$(document).ready(function () {
    // Adjust the number of items per row based on page width
    function adjustDataItemsPerRow() {
        const dataBlock = $('#category-block');
        const dataItems = dataBlock.find('.data-item');
        const dataItemWidth = dataItems.first().outerWidth(true);
        const containerWidth = dataBlock.width();
        const itemsPerRow = Math.floor(containerWidth / dataItemWidth);

        dataItems.css('margin-top', '0'); // Reset margin-top for all items

        dataItems.each(function (index) {
            if (index % itemsPerRow === 0) {
                $(this).css('margin-top', '10px'); // Add margin for new row
            }
        });
    }

    adjustDataItemsPerRow(); // Call on page load

    $(window).resize(function () {
        adjustDataItemsPerRow(); // Adjust on window resize
    });
});

