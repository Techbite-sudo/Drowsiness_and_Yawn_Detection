from django.db import models
from django.contrib.auth.models import AbstractUser



class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("driver", "Driver"),
        ("car_owner", "Car Owner"),
    ]

    user_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="driver",
    )

    class Meta:
        # Your model meta options here
        pass

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_user_permissions",
    )



