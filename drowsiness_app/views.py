import datetime
import os
from django.http import JsonResponse
import time
import cv2
import imutils
from imutils.video import VideoStream
from imutils import face_utils
from scipy.spatial import distance as dist
import numpy as np
import dlib
import pygame.mixer
import asyncio
from asgiref.sync import async_to_sync
from .tasks import drowsiness_detection_task

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import CustomUser, DriverProfile, Alert, UserSettings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

# Global variable to store the running task
running_task = None


def home(request):
    context = {
        "app_name": "DrowsiSense",
        "year": 2023,
    }
    return render(request, "index.html", context)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email")  # Use the email as the username
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("driver_view")
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(request, username=email, password=password)
            login(request, user)
            DriverProfile.objects.create(user=user)
            return redirect("driver_view")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


@login_required
def driver_view(request):
    user = request.user
    driver_profile = DriverProfile.objects.get(user=user)
    alerts = Alert.objects.filter(driver=driver_profile).order_by("-timestamp")
    user_settings = UserSettings.objects.get_or_create(user=user)[0]

    context = {
        "alerts": alerts,
        "user_settings": user_settings,
    }
    return render(request, "driver_dashboard.html", context)


@login_required
def update_settings(request):
    if request.method == "POST":
        user = request.user
        user_settings, created = UserSettings.objects.get_or_create(user=user)

        ear_threshold = request.POST.get("ear_threshold", user_settings.ear_threshold)
        ear_frames = request.POST.get("ear_frames", user_settings.ear_frames)
        yawn_threshold = request.POST.get(
            "yawn_threshold", user_settings.yawn_threshold
        )
        alert_frequency = request.POST.get(
            "alert_frequency", user_settings.alert_frequency
        )

        user_settings.ear_threshold = float(ear_threshold)
        user_settings.ear_frames = int(ear_frames)
        user_settings.yawn_threshold = int(yawn_threshold)
        user_settings.alert_frequency = alert_frequency
        user_settings.save()

        return redirect("driver_dashboard")

    return redirect("driver_dashboard")


@login_required
@csrf_exempt
def toggle_monitoring(request):
    global running_task  # Access the global variable

    if request.method == "POST":
        action = request.POST.get("action", "").lower()
        user = request.user

        if action == "start":
            webcam_index = 0  # Default webcam index
            ear_thresh = user.user_settings.ear_threshold
            ear_frames = user.user_settings.ear_frames
            yawn_thresh = user.user_settings.yawn_threshold

            # Start the real-time drowsiness detection process asynchronously
            running_task = asyncio.create_task(
                drowsiness_detection_task(
                    webcam_index, ear_thresh, ear_frames, yawn_thresh, user
                )
            )

            return JsonResponse(
                {"action": action, "message": "Monitoring started successfully."}
            )
        elif action == "stop":
            # Stop the drowsiness detection process
            if running_task is not None:
                running_task.cancel()
                running_task = None
            return JsonResponse(
                {"action": action, "message": "Monitoring stopped successfully."}
            )
    return JsonResponse({"message": "Invalid request method."})


def logout_view(request):
    logout(request)
    messages.success(request, "Logout successful!")
    return redirect("home")


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear


def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)


def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))

    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))

    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)

    distance = abs(top_mean[1] - low_mean[1])
    return distance
