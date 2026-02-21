"""
Posture Guardian
Detects:
1) If user is too close to screen
2) If user is leaning left or right
"""

import cv2
import mediapipe as mp
import time
import threading
import pygame


class PostureGuardian:

    CHECK_INTERVAL = 10
    VISIBILITY_THRESHOLD = 0.7
    LEAN_THRESHOLD = 0.05
    CLOSE_THRESHOLD = 350

    def __init__(self, shared_state=None):

        self.shared = shared_state
        self.last_alert_time = time.time() + 10

        # Sound
        pygame.mixer.init()
        self.alert_sound = pygame.mixer.Sound("remainder.mp3")

        # Mediapipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose()

        # Camera
        self.cap = cv2.VideoCapture(0)

    def run(self):
        print("[PostureGuardian] Started — monitoring posture...")

        while self.cap.isOpened():

            ret, frame = self.cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            current_time = time.time()

            if results.pose_landmarks:

                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )

                landmarks = results.pose_landmarks.landmark
                frame_width = frame.shape[1]

                bad, message = self.check_posture(landmarks, frame_width)

                if bad and (current_time - self.last_alert_time > self.CHECK_INTERVAL):
                    print(f"[PostureGuardian] ⚠ {message}")
                    self.send_alert()
                    self.last_alert_time = current_time

                if bad:
                    cv2.putText(
                        frame,
                        message,
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2
                    )

            cv2.imshow("Posture Guardian", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def check_posture(self, landmarks, frame_width):

        left = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

        if (left.visibility < self.VISIBILITY_THRESHOLD or
                right.visibility < self.VISIBILITY_THRESHOLD):
            return False, ""

        vertical_diff = abs(left.y - right.y)

        if vertical_diff > self.LEAN_THRESHOLD:
            return True, "Sit straight! Don't lean."

        left_x = int(left.x * frame_width)
        right_x = int(right.x * frame_width)

        shoulder_pixel_distance = abs(left_x - right_x)

        if shoulder_pixel_distance > self.CLOSE_THRESHOLD:
            return True, "Too close! Move back."

        return False, ""

    def send_alert(self):
        threading.Thread(
            target=self.alert_sound.play,
            daemon=True
        ).start()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("[PostureGuardian] Stopped.")
