from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserSignupForm, CustomUserLoginForm, OTPVerificationForm, CustomUserProfileForm
from .models import CustomUser
from .utils import send_verification_email, generate_otp
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .utils import send_password_reset_email
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer 
import logging

logger = logging.getLogger(__name__)

def home(request):
    signup_form = CustomUserSignupForm()
    login_form = CustomUserLoginForm()
    profile_form = CustomUserProfileForm(instance=request.user) if request.user.is_authenticated else None
    return render(request, 'pages/home.html', {
        'signup_form': signup_form,
        'login_form': login_form,
        'profile_form': profile_form,
    })

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only access their own data
        return self.queryset.filter(id=self.request.user.id)
    
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


def signup_view(request):
    if request.method == "POST":
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            # Create the user but deactivate it until email is verified
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(user)
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
                # Log the user in
                login(request, user)
                messages.success(request, "Email verified and login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid OTP or OTP expired.")
    else:
        form = OTPVerificationForm()

    return render(request, 'users/otp_verification.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == "POST":
        form = CustomUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('home')})
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: form.errors[field].as_text() for field in form.errors}
                return JsonResponse({'success': False, 'message': "Profile update failed. Please correct the errors below.", 'errors': errors})
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'pages/home.html', {
                'signup_form': CustomUserSignupForm(),
                'login_form': CustomUserLoginForm(),
                'profile_form': form,
            })
    return redirect('home')

def password_reset_request_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                send_password_reset_email(user, request)
            return JsonResponse({
                'success': True,
                'title': 'Password Reset',
                'message': 'A password reset link has been sent to your email. Please check your inbox.',
                'redirect_url': reverse('home')
            })
    else:
        form = PasswordResetForm()
    return render(request, 'users/forgot_password.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been reset successfully.")
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('home')
                })
            else:
                errors = form.errors.as_json()
                return JsonResponse({
                    'success': False,
                    'message': 'There were errors with your submission.',
                    'errors': errors
                })
        else:
            form = SetPasswordForm(user)
        return render(request, 'users/password_reset.html', {
            'form': form,
            'uidb64': uidb64,
            'token': token
        })
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('home')