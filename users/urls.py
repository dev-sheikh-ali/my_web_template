from django.urls import path, include
from .views import home, profile_view, CustomUserViewSet
from .views_auth import signup_view, login_view, logout_view, activate_account_view, otp_verification_view
from .views_password import password_reset_request_view, password_reset_confirm_view, password_reset_otp_verify_view
from .social_auth_views import custom_google_login, google_login_redirect
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('activate/<uidb64>/<token>/', activate_account_view, name='activate_account'),
    path('otp-verification/', otp_verification_view, name='otp_verification'),
    path('password_reset/', password_reset_request_view, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('api/', include(router.urls)),
    path('accounts/', include('allauth.urls')),
    path('custom-google-login/', custom_google_login, name='custom_google_login'),
    path('google-login-redirect/', google_login_redirect, name='google_login_redirect'),
    path('password_reset_otp/', password_reset_otp_verify_view, name='password_reset_otp_verify'),
]