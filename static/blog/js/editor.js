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
        let formData = new FormData(document.getElementById('articlePublishForm'));
        let publishArticleUrlWithId = publishArticleUrl.replace('0', document.querySelector('#articleNid').value);
        $.ajax({
            type: 'POST',
            url: publishArticleUrlWithId,
            data: formData,
            contentType: false,
            processData: false,
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

// 封面图片上传与预览
document.addEventListener('DOMContentLoaded', function () {
    const coverPreview = document.getElementById('coverPreview');
    const coverInput = document.getElementById('coverUpload');
    const coverOverlayText = document.getElementById('coverOverlayText');

    // 点击图片时触发文件选择器
    coverPreview.addEventListener('click', function () {
        coverInput.click();
    });

    // 点击文字时触发文件选择器
    coverOverlayText.addEventListener('click', function () {
        coverInput.click();
    });

    // 选择文件时预览图片
    coverInput.addEventListener('change', function (event) {
        if (event.target.files && event.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                coverPreview.src = e.target.result;
            }
            reader.readAsDataURL(event.target.files[0]);
        }
    });
});