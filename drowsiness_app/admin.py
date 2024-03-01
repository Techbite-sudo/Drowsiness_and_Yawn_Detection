from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

class UserAdmin(BaseUserAdmin):
    # Add fields to display in the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'user_role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # Remove unnecessary fields from the change form
    readonly_fields = ('last_login',)

    # Customize the list display
    list_display = ('username', 'email', 'user_role', 'is_active', 'is_staff')

    # Filter users by role
    list_filter = ('user_role',)


# Register the custom user model with the admin
admin.site.register(CustomUser, UserAdmin)
