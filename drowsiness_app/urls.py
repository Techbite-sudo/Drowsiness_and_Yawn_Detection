from django.urls import path
from .views import (
    detect_drowsiness,
    register,
    login,
    home,
    logout_view,
    driver_view,
)

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("driver_dashboard/", driver_view, name="driver_dashboard"),
    
]
