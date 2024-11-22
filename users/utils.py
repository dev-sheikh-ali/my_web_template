import secrets
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
import requests
import logging
from smtplib import SMTPException

logger = logging.getLogger(__name__)

def generate_otp():
    return secrets.token_hex(3)  # Generates a 6-character OTP

def send_verification_email(user):
    otp = generate_otp()
    user.otp_code = otp
    user.otp_created_at = timezone.now()
    user.save()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_link = f"{settings.SITE_URL}/activate/{uid}/{token}/"

    subject = "Verify your Email"
    message = f"""
    Hello {user.username},

    Use the following OTP to verify your email address: {otp}

    Or click the link below to verify your email:

    {verification_link}

    Thank you!
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    except (BadHeaderError, SMTPException) as e:
        logger.error(f"Error sending verification email: {e}")
        raise

def send_email(subject, message, recipient_list):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    except (BadHeaderError, SMTPException) as e:
        logger.error(f"Error sending email: {e}")
        raise

def send_password_reset_email(user, request):
    # Generate OTP and save it
    otp = generate_otp()
    user.otp_code = otp
    user.otp_created_at = timezone.now()
    user.save()

    # Generate reset URL
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

    subject = "Password Reset Requested"
    message = f"""
    Hello {user.username},

    You requested a password reset. Use the following OTP to verify your identity: {otp}

    Alternatively, you can reset your password by clicking the link below:

    {reset_url}

    If you didn't request this, you can ignore this email.

    Thank you!
    """
    send_email(subject, message, [user.email])

def get_oauth2_access_token(client_id, client_secret, refresh_token):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }
    response = requests.post(token_url, data=payload)
    response_data = response.json()
    return response_data.get('access_token')