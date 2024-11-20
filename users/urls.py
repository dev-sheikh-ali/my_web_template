from django.urls import path
from .views import (
    signup_view, login_view, logout_view, profile_view,
    home, activate_account_view, otp_verification_view
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('activate/<uidb64>/<token>/', activate_account_view, name='activate_account'),
    path('otp-verification/', otp_verification_view, name='otp_verification'),
]