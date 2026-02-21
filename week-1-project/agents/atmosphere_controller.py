import time
import numpy as np

try:
    import pyaudio
except ImportError:
    pyaudio = None

try:
    import pygame
except ImportError:
    pygame = None


class AtmosphereController:
    # Audio recording parameters
    RATE = 44100          # Sample rate
    CHUNK = 1024          # Samples per buffer
    FORMAT_WIDTH = 2      # 16-bit audio (2 bytes)
    CHANNELS = 1          # Mono
    NOISE_THRESHOLD_DB = 60  # dB threshold

    def __init__(self, shared_state):
        self.shared = shared_state
        self.audio_stream = None
        self.pa = None
        self.threshold_db = self.NOISE_THRESHOLD_DB

    def run(self):
        """Main loop: measure noise and control white noise playback."""
        print("[AtmosphereController] Started — monitoring ambient noise...")

        self.start_microphone()

        while True:
            db_level = self.measure_noise_level()
            self.shared.set("noise_level_db", round(db_level, 1))

            if db_level > self.threshold_db:
                if not self.shared.get("white_noise_playing"):
                    print(f"[AtmosphereController] 🔊 Noise level {db_level:.1f} dB — playing white noise...")
                    self.play_white_noise()
            else:
                if self.shared.get("white_noise_playing"):
                    print(f"[AtmosphereController] 🔇 Noise level dropped to {db_level:.1f} dB — stopping white noise.")
                    self.stop_white_noise()

            time.sleep(1)

    def start_microphone(self):
        """Initialize the PyAudio microphone input stream."""
        if pyaudio is None:
            print("[AtmosphereController] PyAudio not installed — noise monitoring disabled.")
            return

        try:
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
            )
            print("[AtmosphereController] Microphone initialized.")
        except Exception as e:
            print(f"[AtmosphereController] Microphone error: {e}")
            self.audio_stream = None

    def measure_noise_level(self):
        """
        Read audio data from the microphone, calculate RMS,
        and convert to decibels (dB).
        Returns the noise level in dB.
        """
        if self.audio_stream is None:
            return 0

        try:
            audio_data = self.audio_stream.read(self.CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float64)

            # Calculate RMS (Root Mean Square)
            rms = np.sqrt(np.mean(samples ** 2))

            # Avoid log(0) errors
            if rms < 1:
                return 0

            # Convert RMS to decibels
            db = 20 * np.log10(rms)
            return db

        except Exception as e:
            print(f"[AtmosphereController] Audio read error: {e}")
            return 0

    def play_white_noise(self):
        """
        Generate and play white noise using pygame mixer.
        Creates a noise buffer dynamically (no external audio files needed).
        """
        if pygame is None:
            print("[AtmosphereController] pygame not installed — cannot play audio.")
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.RATE, size=-16, channels=1)

            # Generate white noise samples
            duration_sec = 10  # Loop a 10-second clip
            num_samples = self.RATE * duration_sec
            noise_samples = np.random.randint(
                -3000, 3000, size=num_samples, dtype=np.int16
            )

            # Create a pygame Sound from the numpy array
            sound = pygame.sndarray.make_sound(noise_samples)
            sound.play(loops=-1)  # Loop indefinitely

            self.shared.set("white_noise_playing", True)
        except Exception as e:
            print(f"[AtmosphereController] White noise playback error: {e}")

    def stop_white_noise(self):
        """Stop all pygame audio playback."""
        if pygame is None:
            return

        try:
            pygame.mixer.stop()
            self.shared.set("white_noise_playing", False)
        except Exception as e:
            print(f"[AtmosphereController] Error stopping audio: {e}")
