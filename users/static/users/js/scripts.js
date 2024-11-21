$(document).ready(function() {
    // Function to display a message modal with a given message and alert type
    function showMessageModal(message, type) {
        // Sets the body of the modal with a dynamically created alert message
        $('#messageModalBody').html('<div class="alert alert-' + type + '">' + message + '</div>');
        // Shows the modal
        $('#messageModal').modal('show');
    }

    // Function to clear any field-specific error messages
    function clearFieldErrors(formId) {
        // Clears the error message elements for each form field (if any)
        $('#' + formId + ' .field-error').html('');
    }

    // Function to handle form submission via AJAX
    function handleFormSubmit(formId, modalId, successMessage) {
        // Attach a submit event listener to the form
        $('#' + formId).on('submit', function(event) {
            event.preventDefault(); // Prevents the form from being submitted normally
            var form = $(this); // Gets the form object
            var url = form.attr('action'); // Gets the form's action URL
            var formData = form.serialize(); // Serializes the form data for the AJAX request

            // Clear any previous field-specific errors
            clearFieldErrors(formId);

            // Make an AJAX POST request to submit the form data
            $.ajax({
                type: 'POST', // Use POST method
                url: url, // URL to send the request to (form action URL)
                data: formData, // The serialized form data
                success: function(response) {
                    // If the response indicates success
                    if (response.success) {
                        // Hide the modal after successful submission
                        $('#' + modalId).modal('hide');
                        // Show a success message modal with a redirect indication
                        showMessageModal(successMessage + ' Redirecting...', 'success');
                        // After 2 seconds, redirect the user to the provided URL
                        setTimeout(function() {
                            window.location.href = response.redirect_url;
                        }, 2000);
                    } else {
                        // If not successful, show an error message
                        showMessageModal(response.message, 'danger');

                        // Display field-specific errors (if any)
                        $.each(response.errors, function(field, error) {
                            // Set error message for each field in the form
                            $('#error-' + field).html('<div class="text-danger">' + error + '</div>');
                        });
                    }
                },
                error: function(xhr, status, error) {
                    // Show a generic error message if the AJAX request fails
                    showMessageModal('An unexpected error occurred. Please try again later.', 'danger');
                }
            });
        });
    }

    // Attach form submit handlers for different forms on the page
    // These functions are invoked to handle the forms 'signupForm', 'loginForm', and 'profileForm'
    handleFormSubmit('signupForm', 'signupModal', 'Signup successful!');
    handleFormSubmit('loginForm', 'loginModal', 'Login successful!');
    handleFormSubmit('profileForm', 'profileModal', 'Profile updated successfully!');
});
