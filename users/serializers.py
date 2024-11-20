# users/serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'date_of_birth', 'profile_picture_url', 
            'bio', 'is_email_verified', 'is_account_deletion_requested', 
            'consent_given', 'email_notifications_enabled'
        ]
