from django.urls import path
from .views import (
    detect_drowsiness,
    register_view,
    login_view,
    home,
    logout_view,
    driver_view,
)


urlpatterns = [
    path("", home, name="home"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("driver_dashboard/", driver_view, name="driver_dashboard"),
    
]
