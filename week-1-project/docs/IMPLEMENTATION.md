## File Structure

```
deep-work-guardian/
├── main.py
├── shared_state.py
├── agents/
│ ├── **init**.py
│ ├── ergonomics_monitor.py # Member 1 - Muhammad
│ ├── privacy_shield.py # Member 2 - Abdulla
│ ├── atmosphere_controller.py # Member 3 - Shabaz
│ ├── power_optimizer.py # Member 4 - Peshawa
│ └── distraction_blocker.py # Member 5 - Rasyar
└── requirements.txt
```

1. [shared_state.py](#1-shared_statepy)
2. [ergonomics_monitor.py (Muhammad)](#2-ergonomics_monitorpy-muhammad)
3. [privacy_shield.py (Abdullah)](#3-privacy_shieldpy-abdullah)
4. [atmosphere_controller.py (Shabaz)](#4-atmosphere_controllerpy-shabaz)
5. [power_optimizer.py (Peshawa)](#5-power_optimizerpy-peshawa)
6. [distraction_blocker.py (Rasyar)](#6-distraction_blockerpy-rasyar)
7. [main.py](#7-mainpy)

## 1. shared_state.py

A shared state is a single data structure (like a Python dictionary) that exists in the program's memory and all five agents can directly access it to read and write data.

```python
import threading
import time

class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {
            # Ergonomics (Member 1)
            "face_distance_cm": 100,
            "posture_warning_active": False,

            # Privacy (Member 2)
            "background_face_detected": False,
            "screen_blurred": False,

            # Atmosphere (Member 3)
            "noise_level_db": 0,
            "white_noise_playing": False,

            # Power (Member 4)
            "battery_percent": 100,
            "is_charging": True,
            "dark_mode_enabled": False,

            # Distraction (Member 5)
            "active_window": "",
            "distraction_timer": 0,
            "app_blocked": False,

            # Shared webcam frame
            "webcam_frame": None
        }

    def get(self, key):
        with self.lock:
            return self.data.get(key)

    def set(self, key, value):
        with self.lock:
            self.data[key] = value

    def get_all(self):
        with self.lock:
            return self.data.copy()
```

## 2. ergonomics_monitor.py (Muhammad)

Packages used are `cv2` and `player`

```python
class ErgonomicsMonitor:
    def __init__(self, shared_state):
        self.shared = shared_state
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.last_warning_time = 0

    def run(self):
        # Continuous loop
        while True:
            # Get webcam frame from shared state
            frame = self.shared.get("webcam_frame")

            if frame is not None:
                # Detect face
                distance = self.calculate_face_distance(frame)
                self.shared.set("face_distance_cm", distance)

                # Check if too close (< 50cm)
                if distance < 50:
                    self.warn_user_if_needed()

            time.sleep(1)

    def calculate_face_distance(self, frame):
        # Detect faces
        # Calculate distance based on face width
        # Return distance in cm
        pass

    def warn_user_if_needed(self):
        # Check if 2 minutes passed since last warning
        # Send notification using plyer
        pass
```

## 3. privacy_shield.py (Abdullah)

Packages used are `cv2` and `tkinter` and `pygetwindow`

```python
class PrivacyShield:
    def __init__(self, shared_state):
        self.shared = shared_state
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def run(self):
        while True:
            frame = self.shared.get("webcam_frame")

            if frame is not None:
                # Detect multiple faces
                num_faces = self.count_faces(frame)

                if num_faces > 1:
                    self.shared.set("background_face_detected", True)
                    self.blur_screen()
                else:
                    self.shared.set("background_face_detected", False)
                    self.restore_screen()

            time.sleep(0.5)

    def count_faces(self, frame):
        # Detect all faces in frame
        # Return count
        pass

    def blur_screen(self):
        # Minimize all windows OR create blur overlay
        pass

    def restore_screen(self):
        # Restore windows
        pass
```

## 4. atmosphere_controller.py (Shabaz)

Packages used are `pyaudio` and `numpy` and either `pygame` or `playsound`

```python
class AtmosphereController:
    def __init__(self, shared_state):
        self.shared = shared_state
        self.audio_stream = None
        self.threshold_db = 60
        self.mixer = None  # pygame mixer

    def run(self):
        # Initialize microphone
        self.start_microphone()

        while True:
            # Read audio from mic
            db_level = self.measure_noise_level()
            self.shared.set("noise_level_db", db_level)

            # Check threshold
            if db_level > self.threshold_db:
                if not self.shared.get("white_noise_playing"):
                    self.play_white_noise()
            else:
                if self.shared.get("white_noise_playing"):
                    self.stop_white_noise()

            time.sleep(1)

    def start_microphone(self):
        # Initialize PyAudio stream
        pass

    def measure_noise_level(self):
        # Read audio chunk
        # Calculate RMS (Root Mean Square)
        # Convert to decibels
        pass

    def play_white_noise(self):
        # Use pygame to play white_noise.mp3
        self.shared.set("white_noise_playing", True)
        pass

    def stop_white_noise(self):
        # Stop pygame audio
        self.shared.set("white_noise_playing", False)
        pass
```

## 5. power_optimizer.py (Peshawa)

Packages used are `psutil` and `subprocess`

```python
class PowerOptimizer:
    def __init__(self, shared_state):
        self.shared = shared_state
        self.original_brightness = None

    def run(self):
        while True:
            # Get battery info
            battery = psutil.sensors_battery()

            if battery:
                percent = battery.percent
                charging = battery.power_plugged

                self.shared.set("battery_percent", percent)
                self.shared.set("is_charging", charging)

                # Check if unplugged
                if not charging:
                    self.enable_power_saving()
                else:
                    self.restore_normal_mode()

            time.sleep(5)

    def enable_power_saving(self):
        # Enable dark mode
        self.set_dark_mode(True)
        # Lower brightness
        self.lower_brightness()
        self.shared.set("dark_mode_enabled", True)

    def restore_normal_mode(self):
        # Disable dark mode
        self.set_dark_mode(False)
        # Restore brightness
        self.restore_brightness()
        self.shared.set("dark_mode_enabled", False)

    def set_dark_mode(self, enable):
        # Windows: Use subprocess to run PowerShell command
        # macOS: Use subprocess to run AppleScript
        # Linux: Use gsettings
        pass

    def lower_brightness(self):
        # Platform-specific brightness control
        pass

    def restore_brightness(self):
        pass
```

## 6. distraction_blocker.py (Rasyar)

Packages used are `pygetwindow` and `plyer` and `psutil`

```python

class DistractionBlocker:
    def __init__(self, shared_state):
        self.shared = shared_state
        self.blocklist = ["youtube", "instagram", "facebook", "twitter", "tiktok", "game"]
        self.distraction_start_time = None
        self.timeout_seconds = 300  # 5 minutes

    def run(self):
        while True:
            # Get active window
            active_window = self.get_active_window_title()
            self.shared.set("active_window", active_window)

            # Check if distraction
            if self.is_distraction(active_window):
                self.handle_distraction(active_window)
            else:
                # Reset timer
                self.distraction_start_time = None
                self.shared.set("distraction_timer", 0)

            time.sleep(2)

    def get_active_window_title(self):
        # Use pygetwindow to get active window
        pass

    def is_distraction(self, window_title):
        # Check if any blocklist keyword in window title
        return any(blocked in window_title.lower() for blocked in self.blocklist)

    def handle_distraction(self, window_title):
        # Start timer if not started
        if self.distraction_start_time is None:
            self.distraction_start_time = time.time()

        # Calculate elapsed time
        elapsed = time.time() - self.distraction_start_time
        self.shared.set("distraction_timer", elapsed)

        # Check if over 5 minutes
        if elapsed > self.timeout_seconds:
            self.block_app(window_title)

    def block_app(self, window_title):
        # Close or minimize the window
        # Send notification
        self.shared.set("app_blocked", True)
        pass
```

## 7. main.py

```python
import threading
import time
import cv2
from shared_state import SharedState
from agents.ergonomics_monitor import ErgonomicsMonitor
from agents.privacy_shield import PrivacyShield
from agents.atmosphere_controller import AtmosphereController
from agents.power_optimizer import PowerOptimizer
from agents.distraction_blocker import DistractionBlocker

def webcam_capture_thread(shared_state):
    """Shared webcam for Members 1 and 2"""
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if ret:
            shared_state.set("webcam_frame", frame)
        time.sleep(0.1)  # 10 FPS

    cap.release()

def main():
    print("🚀 Starting Deep Work Guardian...\n")

    # Create shared state
    shared = SharedState()

    # Create agents
    ergonomics = ErgonomicsMonitor(shared)
    privacy = PrivacyShield(shared)
    atmosphere = AtmosphereController(shared)
    power = PowerOptimizer(shared)
    distraction = DistractionBlocker(shared)

    # Start webcam thread (shared by Members 1 & 2)
    webcam_thread = threading.Thread(target=webcam_capture_thread, args=(shared,), daemon=True)
    webcam_thread.start()

    # Start all agent threads
    threads = [
        threading.Thread(target=ergonomics.run, daemon=True),
        threading.Thread(target=privacy.run, daemon=True),
        threading.Thread(target=atmosphere.run, daemon=True),
        threading.Thread(target=power.run, daemon=True),
        threading.Thread(target=distraction.run, daemon=True)
    ]

    for thread in threads:
        thread.start()

    print("✅ All subsystems running!")
    print("Press Ctrl+C to stop\n")

    # Keep main thread alive
    try:
        while True:
            # Optional: Print status
            status = shared.get_all()
            print(f"Face Distance: {status['face_distance_cm']}cm | "
                  f"Noise: {status['noise_level_db']}dB | "
                  f"Battery: {status['battery_percent']}% | "
                  f"Active: {status['active_window'][:30]}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()
```
