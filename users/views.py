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
import logging
from django.http import JsonResponse
from django.urls import reverse

logger = logging.getLogger(__name__)

def home(request):
    signup_form = CustomUserSignupForm()
    login_form = CustomUserLoginForm()
    return render(request, 'pages/home.html', {
        'signup_form': signup_form,
        'login_form': login_form
    })

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
                messages.error(request, "Your email is not verified. Please check your inbox.")
            else:
                login(request, user)
                messages.success(request, "Login successful!")
        else:
            messages.error(request, "Invalid username or password.")
    
    return redirect('home')

def signup_view(request):
    if request.method == "POST":
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email is verified
            user.save()

            # Send verification email
            send_verification_email(user)

            request.session['pending_user_id'] = user.id
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': reverse('otp_verification')})
            messages.success(request, "Account created successfully! Please verify your email to activate your account.")
            return redirect('otp_verification')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: form.errors[field].as_text() for field in form.errors}
                return JsonResponse({'success': False, 'message': "Signup failed. Please correct the errors below.", 'errors': errors})
            messages.error(request, "Signup failed. Please correct the errors below.")
            return render(request, 'pages/home.html', {
                'signup_form': form,
                'login_form': CustomUserLoginForm()  # Reset login form as well
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
            return redirect('profile')
    else:
        form = CustomUserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})