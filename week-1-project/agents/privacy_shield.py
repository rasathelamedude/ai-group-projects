"""
Privacy Shield - Member 2 (Abdulla)
Detects if a second person appears near the screen.
If more than 1 face is detected, applies a blur overlay using tkinter
and minimizes all windows. Restores when the stranger leaves.
"""

import time
import cv2
import threading

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import tkinter as tk
except ImportError:
    tk = None


class PrivacyShield:
    def __init__(self, shared_state):
        self.shared = shared_state
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.blur_window = None
        self.blur_active = False
        self.minimized_windows = []

    def run(self):
        """Main loop: continuously check for background faces."""
        print("[PrivacyShield] Started — scanning for unauthorized viewers...")

        while True:
            frame = self.shared.get("webcam_frame")

            if frame is not None:
                num_faces = self.count_faces(frame)

                if num_faces > 1:
                    if not self.shared.get("screen_blurred"):
                        print(f"[PrivacyShield] ⚠ {num_faces} faces detected! Activating privacy mode...")
                        self.shared.set("background_face_detected", True)
                        self.blur_screen()
                else:
                    if self.shared.get("screen_blurred"):
                        print("[PrivacyShield] ✓ Stranger left. Restoring screen...")
                        self.shared.set("background_face_detected", False)
                        self.restore_screen()

            time.sleep(0.5)

    def count_faces(self, frame):
        """Detect all faces in the frame and return the count."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        return len(faces)

    def blur_screen(self):
        """Minimize all windows and create a blur overlay using tkinter."""
        self.shared.set("screen_blurred", True)

        # Minimize all visible windows
        self._minimize_all_windows()

        # Create a fullscreen blur overlay using tkinter (in a separate thread)
        if tk and not self.blur_active:
            self.blur_active = True
            overlay_thread = threading.Thread(target=self._create_blur_overlay, daemon=True)
            overlay_thread.start()

    def restore_screen(self):
        """Remove blur overlay and restore minimized windows."""
        self.shared.set("screen_blurred", False)

        # Close the blur overlay
        self._close_blur_overlay()

        # Restore previously minimized windows
        self._restore_all_windows()

    def _minimize_all_windows(self):
        """Minimize all visible windows using pygetwindow."""
        if gw is None:
            return

        try:
            self.minimized_windows = []
            for window in gw.getAllWindows():
                if window.title and window.visible and not window.isMinimized:
                    try:
                        self.minimized_windows.append(window.title)
                        window.minimize()
                    except Exception:
                        pass
        except Exception as e:
            print(f"[PrivacyShield] Error minimizing windows: {e}")

    def _restore_all_windows(self):
        """Restore previously minimized windows."""
        if gw is None:
            return

        try:
            for title in self.minimized_windows:
                try:
                    windows = gw.getWindowsWithTitle(title)
                    for w in windows:
                        if w.isMinimized:
                            w.restore()
                except Exception:
                    pass
            self.minimized_windows = []
        except Exception as e:
            print(f"[PrivacyShield] Error restoring windows: {e}")

    def _create_blur_overlay(self):
        """Create a semi-transparent fullscreen overlay using tkinter."""
        try:
            root = tk.Tk()
            root.attributes("-fullscreen", True)
            root.attributes("-topmost", True)
            root.attributes("-alpha", 0.85)
            root.configure(bg="black")
            root.overrideredirect(True)

            label = tk.Label(
                root,
                text="🔒 Privacy Mode Active\nScreen hidden for your protection",
                font=("Arial", 28, "bold"),
                fg="white",
                bg="black",
            )
            label.place(relx=0.5, rely=0.5, anchor="center")

            self.blur_window = root
            root.mainloop()
        except Exception as e:
            print(f"[PrivacyShield] Overlay error: {e}")
            self.blur_active = False

    def _close_blur_overlay(self):
        """Close the tkinter blur overlay window."""
        try:
            if self.blur_window:
                self.blur_window.after(0, self.blur_window.destroy)
                self.blur_window = None
            self.blur_active = False
        except Exception as e:
            print(f"[PrivacyShield] Error closing overlay: {e}")
            self.blur_active = False
