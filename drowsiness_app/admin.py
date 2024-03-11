from django.contrib import admin
from .models import DriverProfile, Alert


# Register the custom user model with the admin
admin.site.register(DriverProfile)
admin.site.register(Alert)


