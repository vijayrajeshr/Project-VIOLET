# 🟣 VIOLET: Virtual Intelligence Operations & Logistics Execution Terminal

VIOLET is an advanced, Jarvis-inspired local AI assistant designed to pilot your Windows PC, execute system tasks, automate office operations (PowerPoint/Word document generation), and react to speech/voice directives. 

Unlike conventional LLM chatbots, VIOLET has **"administrator privileges"** enabling hardware control, shell executions, custom script creation, and file manipulations.

---

## 🚀 Key Features

* **PC Piloting & Automation**: Executes shell commands, controls system volumes (via Pycaw) and display brightness, launches applications, and queries processes.
* **Auto-Office Generation**: Writes and executes Python code blocks on-the-fly to create PowerPoint slides (`python-pptx`) and Word documents (`python-docx`).
* **Senses (Hearing & Voice)**:
  * **Ears (STT)**: Voice transcription linking client microphone audio to either high-speed Google SpeechRecognition or local offline OpenAI Whisper.
  * **Mouth (TTS)**: Non-blocking text-to-speech feedback (`pyttsx3`) running in async worker threads.
* **Double Interfaces**:
  * **Cyberpunk Web Dashboard**: Sleek, glassmorphic UI showcasing circular telemetry resource dials (CPU/RAM), quick app buttons, sliders, action console logs, and built-in mic recording.
  * **Rich CLI HUD**: Secured terminal panel display tracking local resources and logging processes.
* **SQLite Persistent Memory**: Automatic dialog tracking to ensure context continuity.

---

## 📁 System Architecture

```
Project-VIOLET/
├── core/
│   ├── __init__.py
│   ├── brain.py       # Core coordinator (Ollama & local HuggingFace adapter patterns)
│   ├── tools.py       # Actions/Tools binder (Subprocess, Pycaw, SBC, PyAutoGUI)
│   ├── ears.py        # Speech-to-Text handler
│   ├── mouth.py       # Text-to-Speech handler
│   └── memory.py      # SQLite memory database (violet_memory.db)
├── interfaces/
│   ├── __init__.py
│   ├── cli.py         # Rich CLI console panel UI
│   └── web.py         # FastAPI web server and routing API
├── templates/
│   └── index.html     # Single-page glassmorphic HTML/JS cyberpunk HUD
├── main.py            # Unified interface launcher entry point
├── requirements.txt   # Consolidated project python dependencies
├── .env.example       # Example workspace configuration file
└── VIOLET.bat         # Windows admin auto-elevator batch script
```

---

## 🛠 Prerequisites

1. **Python 3.10+** (ensure you check the checkbox to *Add Python to PATH* during installation).
2. **Ollama Client** running locally.
   * Download and install from [Ollama.com](https://ollama.com).
   * Pull the default model (e.g. Qwen 2.5 Coder or Llama 3.2):
     ```bash
     ollama pull qwen2.5-coder:latest
     ```

---

## 🏃 Launching VIOLET

### The Simple Windows Way (Recommended)
1. Configure your local parameters in `.env` (copy of `.env.example`).
2. Double click **`VIOLET.bat`**.
   * It will automatically request Administrator elevation (necessary for hardware audio and keyboard hook captures).
   * It runs diagnostic checks verifying Python path and local Ollama link.
   * It prompts you to select the interface: **[1] Web Dashboard** or **[2] CLI Console**.

### The Manual Shell Way
If you want to run the python launcher directly:
* **Web Dashboard**:
  ```bash
  python main.py --web
  ```
  Then open `http://localhost:8000` in your web browser.
* **CLI Terminal Panel**:
  ```bash
  python main.py --cli
  ```
  *(Default authentication passcode code is `admin`)*

---

## 🛡 Security & Failsafes
VIOLET operates with elevated administrator permissions:
- **Corner-Kill**: PyAutoGUI has a built-in safety failsafe enabled. Moving your mouse cursor to any of the four corners of the screen instantly terminates active executing commands.
- **Confirmation Guards**: High-risk system state power controls (Reboot / Shutdown) prompt verification dialogs prior to trigger.
