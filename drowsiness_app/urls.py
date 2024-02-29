from django.urls import path
from .views import detect_drowsiness

urlpatterns = [
    path('detect_drowsiness/', detect_drowsiness, name='detect_drowsiness'),
]