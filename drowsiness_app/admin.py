from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser

class UserAdmin(BaseUserAdmin):
    # Your UserAdmin configuration here
    pass
# Register the custom user model with the admin
admin.site.register(CustomUser, UserAdmin)