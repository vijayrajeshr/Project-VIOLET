import pyttsx3
import whisper
import os

class VioletVoice:
    def __init__(self):
        self.is_muted = False
        self.stt_model = None

    def speak(self, text):
        if self.is_muted:
            return
            
        import threading
        
        def _speak_thread():
            try:
                import pyttsx3
                import pythoncom
                pythoncom.CoInitialize() # Required for COM in threads
                
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                
                selected_voice = None
                for voice in voices:
                    if any(name in voice.name.lower() for name in ["female", "zira", "victoria", "hazel"]):
                        selected_voice = voice.id
                        break
                
                if not selected_voice and voices:
                    selected_voice = voices[0].id
                    
                if selected_voice:
                    engine.setProperty('voice', selected_voice)
                
                engine.setProperty('rate', 175)
                engine.setProperty('volume', 1.0)
                
                # Clean text for TTS
                clean_text = text.replace("*", "").replace("#", "").replace("`", "")
                engine.say(clean_text)
                engine.runAndWait()
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
        """Records audio using sounddevice and returns text using Google STT."""
        try:
            import sounddevice as sd
            from scipy.io.wavfile import write
            import speech_recognition as sr
            import tempfile
            import os
            import winsound
            
            fs = 16000  # Sample rate
            seconds = 5  # 5 seconds recording window
            
            # AUDIO FEEDBACK: Beep to signal "Listening Started"
            winsound.Beep(1000, 200)
            
            # Record
            audio_data = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()  # Wait until recording is finished
            
            # AUDIO FEEDBACK: Double Beep to signal "Listening Stopped / Processing"
            winsound.Beep(800, 150)
            winsound.Beep(800, 150)
            
            # Save to temp file
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            write(temp_path, fs, audio_data)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio = recognizer.record(source)
                
            try:
                text = recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                text = ""
            except sr.RequestError:
                text = ""
                
            try:
                os.remove(temp_path)
            except:
                pass
                
            return text
        except Exception as e:
            return f"Error connecting to microphone: {str(e)}"

if __name__ == "__main__":
    v = VioletVoice()
    v.speak("Voice system check. I am VIOLET. My voice is now configured.")
