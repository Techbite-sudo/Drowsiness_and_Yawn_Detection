# drowsiness_detection/views.py
import os
from django.shortcuts import render
from django.http import JsonResponse
from threading import Thread
import time
import cv2
import imutils
from imutils.video import VideoStream
from imutils import face_utils
from scipy.spatial import distance as dist
import numpy as np
import dlib
import pygame.mixer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
alarm_status = False
alarm_status2 = False
saying = False

def drowsiness_detection(webcam_index, ear_thresh, ear_frames, yawn_thresh):
    global alarm_status
    global alarm_status2
    global saying

    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(BASE_DIR, 'static/music.wav'))

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

    print("-> Loading the predictor and detector...")
    detector = cv2.CascadeClassifier("static/haarcascade_frontalface_default.xml")
    predictor = dlib.shape_predictor("static/shape_predictor_68_face_landmarks.dat")

    print("-> Starting Video Stream")
    vs = VideoStream(src=webcam_index).start()
    time.sleep(1.0)

    COUNTER = 0

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

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

            if ear < ear_thresh:
                COUNTER += 1

                if COUNTER >= ear_frames:
                    if not alarm_status:
                        alarm_status = True
                        t = Thread(target=alarm, args=("wake up sir",))
                        t.daemon = True
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

            if distance > yawn_thresh:
                cv2.putText(
                    frame,
                    "Yawn Alert",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                if not alarm_status2 and not saying:
                    alarm_status2 = True
                    t = Thread(target=alarm, args=("take some fresh air sir",))
                    t.daemon = True
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

# View function
def detect_drowsiness(request):
    # Replace command-line argument parsing with getting parameters from the request
    webcam_index = int(request.GET.get('webcam', 0))
    ear_thresh = float(request.GET.get('ear_thresh', 0.3))
    ear_frames = int(request.GET.get('ear_frames', 30))
    yawn_thresh = int(request.GET.get('yawn_thresh', 20))

    # Use parameters in the code instead of argparse
    drowsiness_thread = Thread(
        target=drowsiness_detection, args=(webcam_index, ear_thresh, ear_frames, yawn_thresh)
    )
    drowsiness_thread.daemon = True
    drowsiness_thread.start()

    return JsonResponse({'status': 'success'})



# # http://127.0.0.1:8000/detect_drowsiness/?webcam=0&ear_thresh=0.3&ear_frames=30&yawn_thresh=20