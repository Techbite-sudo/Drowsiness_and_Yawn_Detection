# drowsiness_detection/views.py
from django.shortcuts import render
from django.http import JsonResponse
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import os
import pygame.mixer
from datetime import datetime


def detect_drowsiness(request):
    # Paste the entire drowsiness detection code here
    pygame.mixer.init()
    pygame.mixer.music.load("static/music.wav")

    # Add these global declarations at the beginning of the views.py file or within the alarm function
    alarm_status = False
    alarm_status2 = False
    saying = False
    
    def alarm(msg):
        global alarm_status
        global alarm_status2
        global saying

        while alarm_status:
            print("Playing audio alert...")
            pygame.mixer.music.play()
            print("call")
            s = 'espeak "' + msg + '"'
            os.system(s)

        if alarm_status2:
            print("Playing audio alert...")
            pygame.mixer.music.play()

            print("call")
            saying = True
            s = 'espeak "' + msg + '"'
            os.system(s)
            saying = False


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


    # Replace command-line argument parsing with getting parameters from the request
    webcam_index = int(request.GET.get('webcam', 0))
    ear_thresh = float(request.GET.get('ear_thresh', 0.3))
    ear_frames = int(request.GET.get('ear_frames', 30))
    yawn_thresh = int(request.GET.get('yawn_thresh', 20))

    # Use parameters in the code instead of argparse
    EYE_AR_THRESH = ear_thresh
    EYE_AR_CONSEC_FRAMES = ear_frames
    YAWN_THRESH = yawn_thresh
    alarm_status = False
    alarm_status2 = False
    saying = False
    COUNTER = 0


    print("-> Loading the predictor and detector...")
    # detector = dlib.get_frontal_face_detector()
    detector = cv2.CascadeClassifier(
        "static/haarcascade_frontalface_default.xml"
    )  # Faster but less accurate
    predictor = dlib.shape_predictor("static/shape_predictor_68_face_landmarks.dat")


    print("-> Starting Video Stream")
    vs = VideoStream(src=webcam_index).start()
    # vs= VideoStream(usePiCamera=True).start()       //For Raspberry Pi
    time.sleep(1.0)

    while True:

        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # rects = detector(gray, 0)
        rects = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        # for rect in rects:
        for x, y, w, h in rects:
            rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            eye = final_ear(shape)
            ear = eye[0]
            leftEye = eye[1]
            rightEye = eye[2]

            distance = lip_distance(shape)

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            lip = shape[48:60]
            cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

            if ear < EYE_AR_THRESH:
                COUNTER += 1

                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    if alarm_status == False:
                        alarm_status = True
                        t = Thread(target=alarm, args=("wake up sir",))
                        t.deamon = True
                        t.start()

                    cv2.putText(
                        frame,
                        "DROWSINESS ALERT!",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

            else:
                COUNTER = 0
                alarm_status = False

            if distance > YAWN_THRESH:
                cv2.putText(
                    frame,
                    "Yawn Alert",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                if alarm_status2 == False and saying == False:
                    alarm_status2 = True
                    t = Thread(target=alarm, args=("take some fresh air sir",))
                    t.deamon = True
                    t.start()
            else:
                alarm_status2 = False

            cv2.putText(
                frame,
                "EAR: {:.2f}".format(ear),
                (300, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            cv2.putText(
                frame,
                "YAWN: {:.2f}".format(distance),
                (300, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()

    return render(request, 'index.html')
