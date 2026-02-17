import time
import pygetwindow as pywindow
import pyautogui
from plyer import notification


class DistractionBlocker:
    def __init__(self, shared_state):
        self.shared = shared_state  # The shared state object passed from the main file
        self.blocklist = ["YouTube", "Instagram", "Facebook", "Twitter", "TikTok"]
        self.distraction_start_time = None  # To track the start time of distraction
        self.timeout_seconds = 300  # 5 minutes timeout

    def run(self):
        while True:
            # get active window
            active_window = self.get_active_window_title()
            self.shared.set("active_window", active_window)

            # check if distraction
            if self.is_distraction(active_window):
                # handle distraction
                self.handle_distraction(active_window)
            else:
                self.distraction_start_time = None
                self.shared.set("distraction_timer", 0)

            time.sleep(2)

    def get_active_window_title(self):
        window = pywindow.getActiveWindow()

        if window is None:
            return ""

        return window.title

    def is_distraction(self, window_title):
        return any(
            keyword.lower() in window_title.lower() for keyword in self.blocklist
        )

    def handle_distraction(self, window_title):
        # Start a timer if there is none
        if self.distraction_start_time is None:
            self.distraction_start_time = time.time()  # start timer

        # calculate how long the user has been distracted
        elapsed = time.time() - self.distraction_start_time
        self.shared.set("distraction_timer", elapsed)

        # if it's over 5 minutes, block the app
        if elapsed > self.timeout_seconds:
            self.block_app(window_title)

    def block_app(self, window_title):
        # if window title includes microsoft edge, chrome or firefox, close tab
        if (
            "Microsoft Edge" in window_title
            or "Chrome" in window_title
            or "Firefox" in window_title
        ):
            pyautogui.hotkey("ctrl", "w")
        else:
            window = pywindow.getActiveWindow()
            if window:
                window.close()

        self.distraction_start_time = None
        self.shared.set("distraction_timer", 0)
        self.shared.set("app_blocked", True)

        # show notification
        notification.notify(
            title="Get Back to Work!",
            message=f"Distraction blocked: {window_title}",
            app_name="Deep Work Guardian",
            timeout=10,
        )
