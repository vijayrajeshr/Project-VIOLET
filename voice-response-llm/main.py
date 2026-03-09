import streamlit as st
from ollama import Client
import whisper
import pyttsx3
import threading # Add this at the top

# 1. INITIALIZE SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. SETUP MODELS & CLIENT
client = Client(host='http://localhost:11434')

@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")

stt_model = load_whisper()

# New: Function to handle voice without crashing the loop
def speak_text(text):
    def _speak():
        # Initialize locally inside the thread to avoid loop errors
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop() # Ensure it shuts down after speaking
    
    # Run voice in a background thread so the UI doesn't freeze
    threading.Thread(target=_speak).start()

# 3. UI LAYOUT
st.title("Vijay's Llama3.2 + Voice Integration project")

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. AUDIO INPUT
audio_value = st.audio_input("Record your question")

if audio_value:
    with st.spinner("Transcribing..."):
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_value.read())
        
        result = stt_model.transcribe("temp_audio.wav")
        user_text = result["text"]

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # 5. GENERATE RESPONSE
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        stream = client.chat(
            model='llama3.2',
            messages=st.session_state.messages,
            stream=True,
        )

        for chunk in stream:
            if 'message' in chunk:
                content = chunk['message']['content']
                full_response += content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        
    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # 6. TRIGGER VOICE (Using the new safe function)
    speak_text(full_response)