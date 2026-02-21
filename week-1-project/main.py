from agents import distraction_blocker
from agents import power_optimizer
from agents import atmosphere_controller
from agents import privacy_shield
import shared_state
import threading
import time


def main():
    print("🚀 Starting Deep Work Guardian...\n")

    shared = shared_state.SharedState()

    distraction = distraction_blocker.DistractionBlocker(shared)
    power = power_optimizer.PowerOptimizer(shared)
    atmosphere = atmosphere_controller.AtmosphereController(shared)
    privacy = privacy_shield.PrivacyShield(shared)
    posture =posture_guardian.PostureGuardian(shared)

    threads = [
        threading.Thread(target=power.run, daemon=True),
        threading.Thread(target=distraction.run, daemon=True),
        threading.Thread(target=atmosphere.run, daemon=True),
        threading.Thread(target=privacy.run, daemon=True),
    ]

    for thread in threads:
        thread.start()

    print("✅ All subsystems running!")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            status = shared.get_all()
            print(
                f"Battery: {status['battery_percent']}% | "
                f"Active: {status['active_window'][:30]}"
            )
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
