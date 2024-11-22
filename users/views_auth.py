# views_auth.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserSignupForm, CustomUserLoginForm, OTPVerificationForm
from .models import CustomUser
from .utils import send_verification_email
import logging

logger = logging.getLogger(__name__)

# signup_view
def signup_view(request):
    if request.method == "POST":
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            # Create the user but deactivate it until email is verified
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            try:
                send_verification_email(user)
            except Exception as e:
                logger.error(f"Error sending verification email: {e}")
                messages.error(request, f"Error sending verification email: {e}")
                return redirect('home')
            request.session['pending_user_id'] = user.id

            # Handle success messages and redirect via AJAX or standard flow
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
                return JsonResponse({'success': True, 'redirect_url': reverse('otp_verification')})
            else:
                messages.success(request, "Account created successfully! Please verify your email to activate your account.")
                return redirect('otp_verification')  # Regular redirect for non-AJAX requests
        else:
            # Handle form errors
            errors = {field: form.errors[field].as_text() for field in form.errors}
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
                return JsonResponse({
                    'success': False,
                    'message': "Signup failed. Please correct the errors below.",
                    'errors': errors
                })

            # Add specific field error messages to the messages framework
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field.capitalize()}: {error}")

            # Render the home page with signup form errors displayed
            return render(request, 'pages/home.html', {
                'signup_form': form,
                'login_form': CustomUserLoginForm(),  # Reset login form
            })

    return redirect('home')

# login view
def login_view(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_email_verified:
                message = "Your email is not verified. Please check your inbox."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': message})
                messages.error(request, message)
                return redirect('home')
            elif user.is_account_deletion_requested:
                if user.is_deletion_period_expired():
                    message = "Your account deletion period has expired. Please contact support."
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': message})
                    messages.error(request, message)
                    return redirect('home')
                else:
                    user.is_account_deletion_requested = False
                    user.account_deletion_requested_at = None
                    user.save()
                    message = "Account deletion undone. Welcome back!"
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'message': message, 'redirect_url': reverse('home')})
                    messages.success(request, message)
                    login(request, user)
                    return redirect('home')
            else:
                login(request, user)
                message = "Login successful!"
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': message, 'redirect_url': reverse('home')})
                messages.success(request, message)
                return redirect('home')
        else:
            # Handle form errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: form.errors[field].as_text() for field in form.errors}
                # Add a general error message if credentials are incorrect
                general_error = form.non_field_errors().as_text()
                return JsonResponse({
                    'success': False,
                    'message': general_error or "Login failed. Please correct the errors below.",
                    'errors': errors
                })

            # For non-AJAX, add detailed errors to the messages framework
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field.capitalize()}: {error}")
            for error in form.non_field_errors():
                messages.error(request, error)

            return render(request, 'pages/home.html', {
                'signup_form': CustomUserSignupForm(),  # Reset signup form
                'login_form': form,  # Pass login form with errors
            })
    return redirect('home')

# logout
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')


# activate_account_view
def activate_account_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        messages.success(request, "Your email has been verified. You can now log in.")
    else:
        messages.error(request, "The activation link is invalid or has expired.")
    
    return redirect('home')

# otp_verification_view is for signup 
def otp_verification_view(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.error(request, "Session expired, please try logging in again.")
        return redirect('home')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            # Check OTP and its expiration time
            if user.otp_code == otp and (timezone.now() - user.otp_created_at) <= timedelta(minutes=10):
                # Clear OTP code
                user.otp_code = None
                user.otp_created_at = None
                user.is_active = True
                user.is_email_verified = True
                user.save()

                # Log the user in and explicitly specify the backend
                login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')

                messages.success(request, "Email verified and login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid OTP or OTP expired.")
    else:
        form = OTPVerificationForm()

    return render(request, 'users/otp_verification.html', {'form': form})

