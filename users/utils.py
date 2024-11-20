import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

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
    message = f"Hello {user.username},\n\nUse the following OTP to verify your email address: {otp}\n\nOr click the link below to verify your email:\n{verification_link}\n\nThank you!"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_password_reset_email(user, reset_link):
    subject = "Password Reset Request"
    message = f"Hello {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nThank you!"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])