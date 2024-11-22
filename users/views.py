# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .forms import CustomUserSignupForm, CustomUserLoginForm, CustomUserProfileForm
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.utils import timezone
from django.contrib.auth import logout
from .utils import send_email
import logging

logger = logging.getLogger(__name__)

# home
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


# profile_view
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

@login_required
def request_account_deletion(request):
    if request.method == "POST":
        user = request.user
        user.is_account_deletion_requested = True
        user.account_deletion_requested_at = timezone.now()
        user.save()
        
        # Log the user out
        logout(request)
        
        # Send email notification
        subject = "Account Deletion Requested"
        message = f"""
        Hello {user.username},

        You have requested to delete your account. If you change your mind, you can undo this action by logging in within 30 days.

        Thank you!
        """
        send_email(subject, message, [user.email])
        
        messages.success(request, "Account deletion requested. You can undo this action by logging in within 30 days.")
        return redirect('home')
    else:
        return render(request, 'users/confirm_account_deletion_modal.html')