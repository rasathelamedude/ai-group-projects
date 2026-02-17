import time
import psutil
import subprocess


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
        try:
            value = 0 if enable else 1
            command = (
                f'Set-ItemProperty -Path '
                f'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize '
                f'-Name AppsUseLightTheme -Value {value}'
            )
            subprocess.run(["powershell", "-Command", command], capture_output=True)
        except Exception as e:
            print(f"[Power] Error setting dark mode: {e}")

    def lower_brightness(self):
        # Platform-specific brightness control
        try:
            command = (
                '(Get-WmiObject -Namespace root/WMI '
                '-Class WmiMonitorBrightnessMethods)'
                '.WmiSetBrightness(1, 30)'
            )
            subprocess.run(["powershell", "-Command", command], capture_output=True)
        except Exception as e:
            print(f"[Power] Error lowering brightness: {e}")

    def restore_brightness(self):
        try:
            command = (
                '(Get-WmiObject -Namespace root/WMI '
                '-Class WmiMonitorBrightnessMethods)'
                '.WmiSetBrightness(1, 80)'
            )
            subprocess.run(["powershell", "-Command", command], capture_output=True)
        except Exception as e:
            print(f"[Power] Error restoring brightness: {e}")
