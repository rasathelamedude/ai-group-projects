import cv2
import mediapipe as mp
import time
import threading  
from win10toast import ToastNotifier
import pygame

pygame.mixer.init()
alert_sound = pygame.mixer.Sound("reminder.mp3") 

toaster = ToastNotifier()

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

CHECK_INTERVAL = 10
SHOULDER_TILT_THRESHOLD = 0.04
VISIBILITY_THRESHOLD = 0.7 

last_alert_time = time.time() + 10
def send_alert(message):
    threading.Thread(
        target=alert_sound.play,  
        daemon=True
    ).start()

def is_posture_bad(landmarks):
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

  
    if left_shoulder.visibility < VISIBILITY_THRESHOLD or right_shoulder.visibility < VISIBILITY_THRESHOLD:
        return False, ""

    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)

    if shoulder_diff > SHOULDER_TILT_THRESHOLD:
        return True, "Fix your posture! Sit straight."

    return False, ""

cap = cv2.VideoCapture(0)
print("Program is Running... Press Q to quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    current_time = time.time()

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        landmarks = results.pose_landmarks.landmark
        bad, message = is_posture_bad(landmarks)

        if bad and (current_time - last_alert_time > CHECK_INTERVAL):
            print(f"⚠️ Bad posture detected: {message}")
            send_alert(message)
            last_alert_time = current_time

        if bad:
            cv2.putText(frame, message, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Deep Working Guardian", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()