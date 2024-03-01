from django.urls import path
from .views import (
    detect_drowsiness,
    register,
    custom_login,
    home,
    logout_view,
    admin_view,
    driver_view,
    car_owner_view,
)

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", custom_login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("admin_dashboard/", admin_view, name="admin_dashboard"),
    path("driver_dashboard/", driver_view, name="driver_dashboard"),
    path("car_owner_dashboard/", car_owner_view, name="car_owner_dashboard"),
    path("detect_drowsiness/", detect_drowsiness, name="detect_drowsiness"),
]
