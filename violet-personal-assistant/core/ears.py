import speech_recognition as sr
from faster_whisper import WhisperModel
import io

class VioletEars:
    def __init__(self, model_size="tiny.en"):
        print(f"VIOLET: Tuning ears to {model_size}...")
        # Run on CPU with INT8 quantization to keep it lightweight
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("VIOLET: Listening...")
            audio = self.recognizer.listen(source)
            
        try:
            # Convert audio data to text using Faster-Whisper
            wav_data = io.BytesIO(audio.get_wav_data())
            segments, _ = self.model.transcribe(wav_data, beam_size=5)
            text = "".join([segment.text for segment in segments]).strip()
            return text
        except Exception as e:
            return f"Error: {str(e)}"

# To test:
# ears = VioletEars()
# print(f"Vijay said: {ears.listen()}")
