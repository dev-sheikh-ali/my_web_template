from django.urls import path, include
from .views import (
    signup_view, login_view, logout_view, profile_view,
    home, activate_account_view, otp_verification_view,
    password_reset_request_view, password_reset_confirm_view
)
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

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
    path('api/', include(router.urls)),  # Include the router URLs
]