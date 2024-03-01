from django.urls import path
from .views import detect_drowsiness,register, custom_login, home

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('detect_drowsiness/', detect_drowsiness, name='detect_drowsiness'),
]