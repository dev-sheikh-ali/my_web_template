$(document).ready(function() {
    $('#signupForm').on('submit', function(event) {
        event.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var formData = form.serialize();

        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            success: function(response) {
                if (response.success) {
                    $('#signupModal').modal('hide');
                    window.location.href = response.redirect_url;
                } else {
                    $('#signupAlertContainer').html('<div class="alert alert-danger">' + response.message + '</div>');
                    $.each(response.errors, function(field, errors) {
                        $('#error-' + field).html(errors.join('<br>'));
                    });
                }
            },
            error: function(xhr, status, error) {
                $('#signupAlertContainer').html('<div class="alert alert-danger">An error occurred. Please try again.</div>');
            }
        });
    });
});