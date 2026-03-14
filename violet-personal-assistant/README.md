Project VIOLET

VIOLET is a next-generation . Unlike standard chatbots, VIOLET is a "Beast" that operates with full system privileges, allowing it to control hardware, navigate the OS, and perceive its environment via vision and voice.

🚀 The Vision
The goal of this project is to create a seamless, fully local AI companion that eliminates the barrier between the user and the machine. VIOLET doesn't just talk; she acts.

Total Control: High-privilege access to terminal, file system, and applications.

Multimodal Senses: Real-time gesture recognition (Eyes) and voice command processing (Ears).

Privacy First: Everything runs locally. No data leaves the machine.

Beast Mode Performance: Optimized for low-resource environments using 4-bit quantization.

🛠 Tech Stack Implementation
🧠 The Brain (Reasoning)
Framework: Hugging Face Transformers + BitsAndBytes

Model: Phi-4-mini (4-bit quantized)

Logic: A custom "Action Bridge" that translates natural language into executable Python scripts.

👁 The Senses (Input)
Vision: MediaPipe & OpenCV for real-time hand tracking and system navigation via gestures.

Hearing: OpenAI Whisper (Distil-Whisper) for near-instant speech-to-text.

Speech: pyttsx3 for expressive, offline text-to-speech feedback.

⚙️ The Hands (Automation)
OS Control: PyAutoGUI for mouse/keyboard emulation.

System Engine: Subprocess for executing high-level shell and terminal commands.

📊 The HUD (Interface)
UI: IPyWidgets (Notebook-based) or CustomTkinter (Standalone).

Monitoring: Psutil for real-time Docker-style CPU and RAM tracking.


🛑 Safety & Failsafe Protocols
With great power comes great responsibility. VIOLET includes built-in safety features:

Master Toggle: A physical UI button to instantly sever the AI's link to system controls.

Corner-Kill: A PyAutoGUI failsafe—slamming the mouse into any screen corner aborts all active commands.

Local Execution: No external APIs are used, ensuring your system's "keys" stay on your drive.

📥 Installation
Clone the Beast:

Bash
git clone <,.........................COMING SOOOOOOON>
cd VIOLET
Install Dependencies:

Bash
pip install -r requirements.txt
Wake VIOLET Up:
Open VIOLET_CORE.ipynb and run all cells.