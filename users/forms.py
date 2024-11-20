from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.core.validators import validate_email
from .models import CustomUser

class CustomUserSignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}), 
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'date_of_birth']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)  # Validate email format
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please choose a different email.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another username.")
        if not username.isalnum():
            raise forms.ValidationError("Username must contain only letters and numbers.")
        return username

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth is None:
            raise forms.ValidationError("Please enter a valid date of birth.")
        # Add custom age validation if needed
        return date_of_birth

class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['date_of_birth', 'profile_picture_url', 'bio', 'email_notifications_enabled']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use by another user.")
        return email

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter the 6-character OTP'})
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isalnum():
            raise forms.ValidationError("OTP must contain only letters and numbers.")
        if len(otp) != 6:
            raise forms.ValidationError("OTP must be exactly 6 characters.")
        return otp

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your registered email'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email.")
        return email

class PasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a new password'}),
        label="New password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your new password'}),
        label="Confirm password"
    )

    class Meta:
        model = CustomUser
        fields = ['new_password1', 'new_password2']