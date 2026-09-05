import os
import io
import tempfile
import speech_recognition as sr

# Safe imports for audio capture
try:
    import sounddevice as sd
    from scipy.io.wavfile import write as wav_write
except ImportError:
    sd = None
    wav_write = None

try:
    import whisper
except ImportError:
    whisper = None

class VioletEars:
    def __init__(self, provider="google", whisper_model_size="tiny"):
        self.provider = provider.lower().strip()
        self.whisper_model_size = whisper_model_size
        self.whisper_model = None
        
        # Pre-load whisper model if requested
        if self.provider == "whisper":
            self.load_whisper_model()

    def load_whisper_model(self):
        """Loads local Whisper model inside memory cache."""
        if not whisper:
            print("[EARS WARNING] Whisper module not installed. Falling back to Google STT.")
            self.provider = "google"
            return
        
        try:
            print(f"[EARS] Loading Whisper model '{self.whisper_model_size}' offline...")
            self.whisper_model = whisper.load_model(self.whisper_model_size)
            print("[EARS] Whisper model loaded successfully.")
        except Exception as e:
            print(f"[EARS ERROR] Failed to load local Whisper model: {e}. Falling back to Google STT.")
            self.provider = "google"

    def transcribe_file(self, wav_path):
        """Transcribes a local WAV audio file using the configured provider."""
        if not os.path.exists(wav_path):
            return "Error: Audio file does not exist."

        # Offline Whisper transcription
        if self.provider == "whisper":
            if not self.whisper_model:
                self.load_whisper_model()
            if self.whisper_model:
                try:
                    result = self.whisper_model.transcribe(wav_path)
                    return result.get("text", "").strip()
                except Exception as e:
                    print(f"[EARS ERROR] Whisper offline transcription failed: {e}. Trying Google STT...")
                    # Fallback to google
            else:
                print("[EARS WARNING] Whisper model is not loaded. Trying Google STT...")

        # Google STT transcription
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return text.strip()
        except sr.UnknownValueError:
            return ""  # No speech detected
        except sr.RequestError as e:
            return f"Error: Speech recognition server offline ({e})"
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"

    def record_audio(self, duration=5, samplerate=16000):
        """Records microphone input to a temporary WAV file path."""
        if not sd or not wav_write:
            return None, "Error: 'sounddevice' or 'scipy' is not installed."
        
        try:
            print(f"[EARS] Recording {duration} seconds...")
            # Capture mono audio
            audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
            sd.wait()  # Wait for recording completion
            
            # Save to temporary WAV file
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            
            wav_write(temp_path, samplerate, audio_data)
            return temp_path, None
        except Exception as e:
            return None, f"Error recording microphone audio: {str(e)}"

    def record_and_transcribe(self, duration=5):
        """Records from local mic and returns the transcribed text."""
        wav_path, err = self.record_audio(duration)
        if err:
            return f"Audio Error: {err}"
        if not wav_path:
            return "Audio Error: Unknown recording error."
        
        try:
            transcription = self.transcribe_file(wav_path)
            # Clean up temp file
            os.remove(wav_path)
            return transcription
        except Exception as e:
            return f"Transcription error: {str(e)}"

if __name__ == "__main__":
    ears = VioletEars(provider="google")
    print("[SYSTEM] Speak into your microphone now for a quick test...")
    result = ears.record_and_transcribe(4)
    print(f"[SYSTEM] Transcribed result: '{result}'")
