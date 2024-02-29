# drowsiness_detection/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

# create your models here


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
