"""
Power Optimizer - Member 4 (Peshawa)
Monitors battery status and charging state.
When unplugged: enables Windows Dark Mode + lowers brightness to 30%.
When plugged back in: restores Light Mode + brightness to 80%.
Uses state tracking to avoid spamming commands every loop.
"""

import time
import subprocess

try:
    import psutil
except ImportError:
    psutil = None


class PowerOptimizer:
    BRIGHTNESS_LOW = 30      # Brightness when on battery
    BRIGHTNESS_NORMAL = 80   # Brightness when plugged in

    def __init__(self, shared_state):
        self.shared = shared_state
        self.last_power_state = None  # Track previous state to avoid spam

    def run(self):
        """Main loop: monitor battery and toggle power-saving settings."""
        print("[PowerOptimizer] Started — monitoring battery status...")

        while True:
            if psutil is None:
                time.sleep(5)
                continue

            battery = psutil.sensors_battery()

            if battery:
                percent = battery.percent
                charging = battery.power_plugged

                self.shared.set("battery_percent", percent)
                self.shared.set("is_charging", charging)

                # Only act on state TRANSITIONS (not every loop)
                if charging != self.last_power_state:
                    if not charging:
                        print(f"[PowerOptimizer] 🔋 Unplugged ({percent}%) — enabling power saving mode...")
                        self.enable_power_saving()
                    else:
                        print(f"[PowerOptimizer] ⚡ Plugged in ({percent}%) — restoring normal mode...")
                        self.restore_normal_mode()

                    self.last_power_state = charging

            time.sleep(5)

    def enable_power_saving(self):
        """Enable dark mode and lower brightness for battery saving."""
        self.set_dark_mode(True)
        self.set_brightness(self.BRIGHTNESS_LOW)
        self.shared.set("dark_mode_enabled", True)

    def restore_normal_mode(self):
        """Disable dark mode and restore brightness."""
        self.set_dark_mode(False)
        self.set_brightness(self.BRIGHTNESS_NORMAL)
        self.shared.set("dark_mode_enabled", False)

    def set_dark_mode(self, enable):
        """
        Toggle Windows Dark/Light Mode via the Registry using PowerShell.
        Sets both App and System themes.
        """
        value = 0 if enable else 1  # Registry: 0 = Dark, 1 = Light
        mode_name = "Dark" if enable else "Light"

        commands = [
            # Set App theme
            (
                f'Set-ItemProperty -Path '
                f'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize '
                f'-Name AppsUseLightTheme -Value {value}'
            ),
            # Set System theme
            (
                f'Set-ItemProperty -Path '
                f'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize '
                f'-Name SystemUsesLightTheme -Value {value}'
            ),
        ]

        for cmd in commands:
            try:
                subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True,
                    timeout=10,
                )
            except Exception as e:
                print(f"[PowerOptimizer] Error setting {mode_name} Mode: {e}")

        print(f"[PowerOptimizer] {mode_name} Mode enabled.")

    def set_brightness(self, level):
        """
        Set screen brightness using PowerShell WMI command.
        Level should be 0-100.
        """
        cmd = (
            f'(Get-WmiObject -Namespace root/WMI '
            f'-Class WmiMonitorBrightnessMethods)'
            f'.WmiSetBrightness(1, {level})'
        )

        try:
            subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                timeout=10,
            )
            print(f"[PowerOptimizer] Brightness set to {level}%.")
        except Exception as e:
            print(f"[PowerOptimizer] Error setting brightness: {e}")
