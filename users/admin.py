from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # List the fields to display in the user list page
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_email_verified', 'date_of_birth')
    
    # Add filters to narrow down the results based on certain fields
    list_filter = ('is_staff', 'is_active', 'is_email_verified', 'groups', 'user_permissions')
    
    # Define the fieldsets for the user detail page
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'profile_picture_url', 'bio')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Email Verification', {'fields': ('is_email_verified',)}),
        ('Account Management', {'fields': ('is_account_deletion_requested', 'consent_given', 'email_notifications_enabled')}),
    )
    
    # Add fieldsets for creating new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'groups', 'user_permissions')
        }),
    )
    
    # Enable search by specific fields
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Define the ordering of the user list
    ordering = ('username',)
    
    # Enable horizontal filtering for many-to-many fields
    filter_horizontal = ('groups', 'user_permissions')

# Register the CustomUser model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
