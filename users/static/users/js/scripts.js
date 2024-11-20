// static/users/js/scripts.js
$(document).ready(function() {
    function showMessageModal(message, type) {
        $('#messageModalBody').html('<div class="alert alert-' + type + '">' + message + '</div>');
        $('#messageModal').modal('show');
    }

    function handleFormSubmit(formId, modalId, successMessage) {
        $('#' + formId).on('submit', function(event) {
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
                        $('#' + modalId).modal('hide');
                        showMessageModal(successMessage + ' Redirecting...', 'success');
                        setTimeout(function() {
                            window.location.href = response.redirect_url;
                        }, 2000);
                    } else {
                        showMessageModal(response.message, 'danger');
                        $.each(response.errors, function(field, errors) {
                            $('#error-' + field).html(errors.join('<br>'));
                        });
                    }
                },
                error: function(xhr, status, error) {
                    showMessageModal('An error occurred. Please try again.', 'danger');
                }
            });
        });
    }

    handleFormSubmit('signupForm', 'signupModal', 'Signup successful!');
    handleFormSubmit('loginForm', 'loginModal', 'Login successful!');
    handleFormSubmit('profileForm', 'profileModal', 'Profile updated successfully!');
});