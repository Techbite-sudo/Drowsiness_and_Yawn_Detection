import asyncio
import os
import cv2
import dlib
import imutils
import pygame.mixer
from imutils import face_utils
from imutils.video import VideoStream
from scipy.spatial import distance as dist
from .models import Alert

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def drowsiness_detection_task(
    webcam_index, ear_thresh, ear_frames, yawn_thresh, user
):
    print("Drowsiness detection task started.")
    alarm_status = False
    alarm_status2 = False
    saying = False

    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(BASE_DIR, "static/music.wav"))

    def alarm(msg):
        nonlocal alarm_status, alarm_status2, saying

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

        # Create an alert instance and save it to the database
        alert = Alert(user=user, alert_type="drowsiness", description=msg)
        alert.save()

    print("-> Loading the predictor and detector...")
    detector = cv2.CascadeClassifier("static/haarcascade_frontalface_default.xml")
    predictor = dlib.shape_predictor("static/shape_predictor_68_face_landmarks.dat")

    print("-> Starting Video Stream")
    try:
        vs = VideoStream(src=webcam_index).start()
        print("Video stream opened successfully.")
    except Exception as e:
        print(f"Error opening video stream: {e}")
        return  # Exit the function if the video stream cannot be opened

    await asyncio.sleep(1.0)  # Allow the video stream to warm up

    COUNTER = 0

    while True:
        frame = vs.read()
        if frame is None:
            print("Error: No video frame received.")
            break

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
                        msg = "Drowsiness detected!"
                        alarm(msg)

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
                msg = "Yawn Alert"
                if not alarm_status2 and not saying:
                    alarm_status2 = True
                    alarm(msg)

                cv2.putText(
                    frame,
                    "Yawn Alert",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
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

        await asyncio.sleep(0)  # Allow the async context to switch

    cv2.destroyAllWindows()
    vs.stop()
    print("Drowsiness detection task completed.")
