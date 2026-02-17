import threading


class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {
            # Ergonomics
            "face_distance_cm": 100,
            "posture_warning_active": False,
            # Privacy
            "background_face_detected": False,  # True if a face is detected in the background
            "screen_blurred": False,  # True if the screen is blurred
            # Backgournd Noise
            "noise_level_db": 0,
            "white_noise_playing": False,
            # Power
            "battery_percent": 100,
            "is_charging": True,
            "dark_mode_enabled": False,
            # Distraction
            "active_window": "",  # Title of the active window
            "distraction_timer": 0,  # Time in seconds the user has been distracted
            "app_blocked": False,  # True if the app is blocked
            # Shared webcam
            "webcam_frame": None,
        }

    def get(self, key):
        with self.lock:
            return self.data[key]

    def set(self, key, value):
        with self.lock:
            self.data[key] = value

    def get_all(self):
        with self.lock:
            return self.data.copy()
