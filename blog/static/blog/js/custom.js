$('.clickable-card').click(function (e) {
    console.log(e.target);
    if (!$(e.target).closest('a').length) {
        window.location.href = $(this).data('url');
    }
});