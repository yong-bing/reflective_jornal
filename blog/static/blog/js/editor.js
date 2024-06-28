$(document).ready(function () {
    let modal = $('#publishModal');
    let backdrop = $('#modalBackdrop');
    let openModalButton = $('#publishButton');
    let closeModalButtons = $('#closeModal, #closeModalFooter');
    let csrfmiddlewaretoken = $('[name="csrfmiddlewaretoken"]').val();

    function openModal() {
        modal.addClass('show').css('display', 'block');
        backdrop.addClass('show').css('display', 'block');
        $('body').addClass('modal-open');
    }

    function closeModal() {
        modal.removeClass('show').css('display', 'none');
        backdrop.removeClass('show').css('display', 'none');
        $('body').removeClass('modal-open');
    }

    $('#saveDraft').click(function (e) {
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

    openModalButton.click(function (e) {
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

    closeModalButtons.click(closeModal);
    backdrop.click(closeModal);

    $('#confirmPublish').click(function (e) {
        let formData = new FormData($('#articlePublishForm')[0]);
        let publishArticleUrlWithId = publishArticleUrl.replace('0', $('#articleNid').val());
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

    // 封面图片上传与预览
    const $coverPreview = $('#coverPreview');
    const $coverInput = $('#coverUpload');
    const $coverOverlayText = $('#coverOverlayText');

    // 点击图片或文字时触发文件选择器
    $coverPreview.add($coverOverlayText).click(function () {
        $coverInput.click();
    });

    // 选择文件时预览图片
    $coverInput.change(function (event) {
        if (event.target.files && event.target.files[0]) {
            let reader = new FileReader();
            reader.onload = function (e) {
                $coverPreview.attr('src', e.target.result);
            }
            reader.readAsDataURL(event.target.files[0]);
        }
    });
});