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

// $(document).ready(function () {
//     // Adjust the number of items per row based on page width
//     function adjustDataItemsPerRow() {
//         const dataBlock = $('#category-block');
//         const dataItems = dataBlock.find('.data-item');
//         const dataItemWidth = dataItems.first().outerWidth(true);
//         const containerWidth = dataBlock.width();
//         const itemsPerRow = Math.floor(containerWidth / dataItemWidth);
//
//         dataItems.css('margin-top', '0'); // Reset margin-top for all items
//
//         dataItems.each(function (index) {
//             if (index % itemsPerRow === 0) {
//                 $(this).css('margin-top', '10px'); // Add margin for new row
//             }
//         });
//     }
//
//     adjustDataItemsPerRow(); // Call on page load
//
//     $(window).resize(function () {
//         adjustDataItemsPerRow(); // Adjust on window resize
//     });
// });


$(document).ready(function () {
    let modal = $('#publishModal');
    let backdrop = $('#modalBackdrop');
    let openModalButton = $('#publishButton');
    let closeModalButtons = $('#closeModal, #closeModalFooter');
    let csrfmiddlewaretoken = $('[name="csrfmiddlewaretoken"]').val();

    function openModal() {
        modal.addClass('show');
        modal.css('display', 'block');
        backdrop.addClass('show');
        backdrop.css('display', 'block');
        $('body').addClass('modal-open');
    }

    function closeModal() {
        modal.removeClass('show');
        modal.css('display', 'none');
        backdrop.removeClass('show');
        backdrop.css('display', 'none');
        $('body').removeClass('modal-open');
    }

    $('#saveDraft').on('click', function (e) {
        e.preventDefault();
        let form = $('#articleCreateForm');
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize() + '&save_draft=true',
            headers: {
                'X-CSRFToken': csrfmiddlewaretoken
            },
            success: function (response) {
                if (response.status === 'success') {
                    window.location.href = '/dashboard/';
                }
            },
            error: function (response) {
                alert('存为草稿失败，请检查输入内容。');
            }
        });
    });

    openModalButton.on('click', function (e) {
        e.preventDefault();
        let form = $('#articleCreateForm');
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize() + '&publish=true',
            headers: {
                'X-CSRFToken': csrfmiddlewaretoken
            },
            success: function (response) {
                $('#articleNid').val(response.nid);
                openModal();
            },
            error: function (response) {
                alert('存在错误，请检查输入内容。');
            }
        });
    });

    closeModalButtons.on('click', function () {
        closeModal();
    });

    backdrop.on('click', function () {
        closeModal();
    });

    $('#confirmPublish').on('click', function () {
        let form = $('#articlePublishForm');
        $.ajax({
            type: 'POST',
            url: '{% url "publish_article" 0 %}'.replace('0', form.find('#articleNid').val()),
            data: form.serialize(),
            headers: {
                'X-CSRFToken': csrfmiddlewaretoken
            },
            success: function (response) {
                if (response.status === 'success') {
                    window.location.href = '/dashboard/';
                }
            },
            error: function (response) {
                alert('发布失败，请检查输入内容。');
            }
        });
    });
});

document.querySelector('.cover-upload').addEventListener('click', function () {
    document.getElementById('cover').click();
});

document.getElementById('cover').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('coverPreview').src = e.target.result;
        }
        reader.readAsDataURL(file);
    }
});
