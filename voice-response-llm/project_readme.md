# Vijay's Llama3.2 + Voice Integration Project (Locally runnable)
A sleek, local, and private voice assistant that feels like Google Gemini. Speak to your computer, see your words appear in real-time, and watch Llama 3.2 stream its response back to you with a high-quality voice.

---
# How to run this on Docker? 
The Docker Way (Recommended)
This is the best way to ensure all the audio and voice tools work perfectly without messing up your Windows/Mac settings.

Open your Terminal (PowerShell or Command Prompt) in your project folder.

Build the Image (This "packages" your code and tools):

Bash
docker build -t llama-voice-app .
Run the Container:

Bash
docker run -d -p

---

# Features
Real-Time Transcription: Uses OpenAI's Whisper to turn your speech into text instantly.

Lively UI: A beautiful Streamlit dashboard that shows your conversation history.

Streaming Responses: Text pops up word-by-word just like the high-end AI models.

Voice-Back: Automatically speaks the AI's response aloud.

100% Local: Your data never leaves your machine.

# The Tech Stack
Brain: Ollama (Running Llama 3.2)

Ears: OpenAI Whisper

Voice: pyttsx3 (Offline Text-to-Speech)

Face: Streamlit (The UI framework)

 Getting Started
1. Prerequisites
Make sure you have Ollama installed and the model downloaded:

Bash
ollama run llama3.2
2. Installation
Clone this folder and install the necessary Python libraries:

Bash
pip install streamlit ollama openai-whisper pyttsx3
3. Usage
Run the application using the following command:

Bash
streamlit run main.py
🖥️ How it Works
Click the Mic: Record your question directly in the browser.

Speech-to-Text: Whisper converts your audio into a text prompt.

LLM Processing: Llama 3.2 generates a response based on your query.

Live Stream: You see the response "typing" onto the screen in real-time.

Audio Playback: Your computer reads the answer back to you.
