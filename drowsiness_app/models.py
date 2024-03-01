# models.py in drowsiness_app

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Your custom fields and methods here

    class Meta:
        # Your model meta options here
        pass
    
# Add related names to avoid clashes
CustomUser._meta.get_field('groups').related_name = 'customuser_groups'
CustomUser._meta.get_field('user_permissions').related_name = 'customuser_user_permissions'






# from django.db import models
# from django.contrib.auth.models import AbstractUser
# # create your models here


# class CustomUser(AbstractUser):
#     ROLE_CHOICES = [
#         ("admin", "Admin"),
#         ("driver", "Driver"),
#         ("car_owner", "Car Owner"),
#     ]

#     user_role = models.CharField(
#         max_length=20,
#         choices=ROLE_CHOICES,
#         default="driver",
#     )
