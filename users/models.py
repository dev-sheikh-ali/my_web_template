from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture_url = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_account_deletion_requested = models.BooleanField(default=False)
    account_deletion_requested_at = models.DateTimeField(blank=True, null=True)  # New field
    consent_given = models.BooleanField(default=True)
    email_notifications_enabled = models.BooleanField(default=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    # Fixing groups field conflict
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Ensure no clashes in reverse accessor
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    # Fixing user_permissions field conflict
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Ensure no clashes in reverse accessor
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username

    def is_deletion_period_expired(self):
        if self.account_deletion_requested_at:
            return timezone.now() > self.account_deletion_requested_at + timedelta(days=30)
        return False