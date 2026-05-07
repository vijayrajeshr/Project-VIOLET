import pyttsx3
import whisper
import os

class VioletVoice:
    def __init__(self):
        self.tts_engine = None
        self.is_muted = False
        self._init_tts()
        self.stt_model = None

    def _init_tts(self):
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            
            # Priority: Find a female voice
            selected_voice = None
            for voice in voices:
                # Check for "female" or specific names like "Zira" (Windows) or "Victoria" (Mac)
                if any(name in voice.name.lower() for name in ["female", "zira", "victoria", "hazel"]):
                    selected_voice = voice.id
                    break
            
            if not selected_voice and voices:
                selected_voice = voices[0].id # Fallback to first available
                
            if selected_voice:
                self.tts_engine.setProperty('voice', selected_voice)
            
            self.tts_engine.setProperty('rate', 175) # Slightly slower for clarity
            self.tts_engine.setProperty('volume', 1.0)
            
        except Exception as e:
            print(f"TTS Initialization Warning: {e}")
            self.tts_engine = None

    def speak(self, text):
        if self.is_muted:
            return
            
        if self.tts_engine:
            import threading
            
            def _speak_thread():
                try:
                    # Clean text for TTS (remove markdown or special symbols)
                    clean_text = text.replace("*", "").replace("#", "").replace("`", "")
                    self.tts_engine.say(clean_text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    pass
            
            # Run speech in a background thread to prevent UI blocking
            thread = threading.Thread(target=_speak_thread)
            thread.daemon = True
            thread.start()

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        return self.is_muted

    def listen(self):
        """Records audio from the microphone and returns text using Google STT for speed."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                # Calibrate for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Use Google Speech Recognition for fast local processing without heavy local models
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            return f"Error connecting to microphone: {str(e)}"

if __name__ == "__main__":
    v = VioletVoice()
    v.speak("Voice system check. I am VIOLET. My voice is now configured.")
