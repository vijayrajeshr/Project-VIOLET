import threading

# Safe import for local TTS library
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

class VioletMouth:
    def __init__(self, enabled=True, speech_rate=175, volume=1.0):
        self.enabled = enabled
        self.speech_rate = speech_rate
        self.volume = volume

    def speak(self, text):
        """Speaks the input text aloud using a non-blocking background thread."""
        if not self.enabled or not pyttsx3:
            print(f"[MOUTH SILENT] VIOLET: {text}")
            return

        def _speak_thread():
            # Initialize COM libraries inside the child thread on Windows
            import os
            if os.name == 'nt':
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except ImportError:
                    pass
            
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', self.speech_rate)
                engine.setProperty('volume', self.volume)
                
                # Check for female voice id options
                voices = engine.getProperty('voices')
                selected_voice = None
                for voice in voices:
                    name_lower = voice.name.lower()
                    if any(x in name_lower for x in ["female", "zira", "victoria", "hazel", "siri"]):
                        selected_voice = voice.id
                        break
                
                if not selected_voice and voices:
                    selected_voice = voices[0].id
                
                if selected_voice:
                    engine.setProperty('voice', selected_voice)
                
                # Strip clean readable text from Markdown tags
                clean_text = text.replace("*", "").replace("#", "").replace("`", "").replace("_", "")
                
                engine.say(clean_text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"[MOUTH ERROR] Local speech synthesis failed: {e}")

        # Run speech asynchronously to avoid blocking the main server/client thread
        thread = threading.Thread(target=_speak_thread)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    mouth = VioletMouth(enabled=True)
    mouth.speak("Vocal synthesis initialization test. Operational.")
    import time
    time.sleep(3) # Wait for thread completion
