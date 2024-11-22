from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
from allauth.account.utils import perform_login
from .models import CustomUser
from .utils import send_verification_email
from urllib.parse import urlencode
import requests
import logging

logger = logging.getLogger(__name__)

def google_login_redirect(request):
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(settings.SOCIALACCOUNT_PROVIDERS['google']['SCOPE']),
        'access_type': 'offline',
        'prompt': 'consent',
    }
    url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return redirect(url)

def custom_google_login(request):
    code = request.GET.get('code')
    if not code:
        return redirect('google_login_redirect')

    adapter = GoogleOAuth2Adapter(request)
    client = OAuth2Client(
        request,
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        access_token_method='POST',
        access_token_url='https://oauth2.googleapis.com/token',
        callback_url=settings.GOOGLE_REDIRECT_URI
    )
    try:
        token = client.get_access_token(code)
    except Exception as e:
        logger.error(f"Error retrieving access token: {e}")
        return redirect('home')

    access_token = token['access_token']

    # Make a request to the Google UserInfo endpoint
    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'access_token': access_token}
    )
    user_info = user_info_response.json()

    try:
        # Check if the user already exists
        social_account = SocialAccount.objects.get(uid=user_info['id'])
        user = social_account.user
    except SocialAccount.DoesNotExist:
        # If the user does not exist, create a new user
        base_username = user_info['email'].split('@')[0]
        username = base_username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = CustomUser.objects.create(
            username=username,
            email=user_info['email'],
            is_active=False,  # Set to False until email is verified
            is_email_verified=False
        )
        social_account = SocialAccount.objects.create(
            user=user,
            uid=user_info['id'],
            provider='google'
        )
        user.set_unusable_password()
        user.save()
        try:
            send_verification_email(user)  # Send verification email
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            return redirect('home')

    # Set the pending user ID in the session
    request.session['pending_user_id'] = user.id

    # Log the user in
    perform_login(request, user, email_verification=settings.ACCOUNT_EMAIL_VERIFICATION)
    
    return redirect('otp_verification')