import pyttsx3

class VioletMouth:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.set_voice()

    def set_voice(self):
        voices = self.engine.getProperty('voices')
        # Usually index 1 is a female voice, 0 is male.
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id) 
        elif len(voices) > 0:
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 180) # Speaking speed

    def speak(self, text):
        print(f"VIOLET: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

# To test:
# mouth = VioletMouth()
# mouth.speak("System systems are fully operational, Vijay.")
