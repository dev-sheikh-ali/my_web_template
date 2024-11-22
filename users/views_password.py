from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import CustomUser
from .utils import send_password_reset_email
import logging
logger = logging.getLogger(__name__)

# For requesting a password reset
def password_reset_request_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                # Send password reset email and OTP (Make sure the send_password_reset_email function is defined)
                try:
                    send_password_reset_email(user, request)
                except Exception as e:
                    logger.error(f"Error sending password reset email: {e}")
                    messages.error(request, f"Error sending password reset email: {e}")
                    return redirect('home')
                
                # Return a JSON response indicating success
                return JsonResponse({
                    'success': True,
                    'message': 'A password reset link and OTP have been sent to your email. Please check your inbox.',
                    'redirect_url': reverse('password_reset_otp_verify')  # Redirect to the OTP verification page
                })
    else:
        form = PasswordResetForm()
    return render(request, 'users/forgot_password.html', {'form': form})

# For confirming password reset using the link or OTP
def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and (default_token_generator.check_token(user, token) or user.otp_code == request.POST.get('otp')):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                user.otp_code = None  # Clear the OTP after successful password reset
                user.save()
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
        messages.error(request, "The password reset link or OTP is invalid or has expired.")
        return redirect('home')

def password_reset_otp_verify_view(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        user = CustomUser.objects.filter(otp_code=otp).first()
        if user and user.otp_code == otp:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            return JsonResponse({
                'success': True,
                'redirect_url': reset_url
            })
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return JsonResponse({
                'success': False,
                'message': 'Invalid OTP. Please try again.'
            })
    return render(request, 'users/password_reset_otp.html')