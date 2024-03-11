from django.db import models
from django.contrib.auth.models import User


class DriverProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="driver_profile"
    )
    license_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Alert(models.Model):
    driver = models.ForeignKey(
        DriverProfile, on_delete=models.CASCADE, related_name="alerts"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(
        max_length=50,
        choices=(
            ("drowsiness", "Drowsiness"),
            ("yawning", "Excessive Yawning"),
            # Add more alert types as needed
        ),
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.alert_type} - {self.driver.user.username} ({self.timestamp})"
