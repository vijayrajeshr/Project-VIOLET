import pyautogui
import subprocess
import os

class VioletHands:
    def __init__(self):
        # Safety: If something goes wrong, move mouse to corner to kill
        pyautogui.FAILSAFE = True 

    def execute_terminal(self, command):
        """Runs a system-level shell command."""
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode()
        except Exception as e:
            return str(e)

    def type_message(self, text):
        """Types text as if VIOLET has a physical keyboard."""
        pyautogui.write(text, interval=0.01)

    def open_application(self, app_name):
        """Platform independent app launcher."""
        if os.name == 'nt': # Windows
            os.system(f"start {app_name}")
        else: # Mac/Linux
            os.system(f"open -a {app_name}")

# Initialize VIOLET's physical capabilities
hands = VioletHands()
