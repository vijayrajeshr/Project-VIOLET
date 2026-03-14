import streamlit as st
import psutil
import time

st.set_page_config(page_title="VIOLET | Core", page_icon="🟣", layout="wide")

# Custom CSS for the "Beast" look
st.markdown("""
<style>
    .stApp {
        background-color: #0f0f13;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #7c4dff;
        color: white;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #651fff;
        box-shadow: 0 0 15px rgba(101, 31, 255, 0.4);
    }
    .violet-header {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(90deg, #b388ff, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
    }
    .violet-subheader {
        color: #888;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="violet-header">VIOLET</div>', unsafe_allow_html=True)
st.markdown('<div class="violet-subheader">Personal Assistant</div>', unsafe_allow_html=True)

@st.cache_resource
def load_modules():
    modules = {}
    try:
        from core.brain import VioletBrain
        modules['brain'] = VioletBrain()
        
        from core.mouth import VioletMouth
        modules['mouth'] = VioletMouth()
        
        from automation.system_ctl import VioletHands
        modules['hands'] = VioletHands()
        
    except Exception as e:
        st.error(f"Error loading modules: {e}")
    return modules

if 'system_active' not in st.session_state:
    st.session_state.system_active = False

if 'logs' not in st.session_state:
    st.session_state.logs = ["System Initialized. Waiting for BEAST MODE activation."]

def add_log(msg, sender="System"):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {sender}: {msg}")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.button("Initiate VIOLET", use_container_width=True):
        st.session_state.system_active = not st.session_state.system_active
        if st.session_state.system_active:
            add_log("Beast Mode Engaged. Waking up DeepSeek Matrix...", "System")
        else:
            add_log("VIOLET entering standby...", "System")

with col2:
    st.metric("CPU Utilization", f"{psutil.cpu_percent()}%")

with col3:
    st.metric("RAM Allocation", f"{psutil.virtual_memory().percent}%")

modules = None
if st.session_state.system_active:
    st.success("🟢 VIOLET ONLINE")
    with st.spinner("Initializing DeepSeek Synapses..."):
        modules = load_modules()
        if 'notified' not in st.session_state:
            add_log("Brain matrix online. I am ready.", "VIOLET")
            if 'mouth' in modules:
                modules['mouth'].speak("Brain matrix online. I am ready.")
            st.session_state.notified = True
else:
    st.error("🔴 VIOLET OFFLINE")

st.markdown("### Command Terminal")
log_container = st.container(height=300)
with log_container:
    for log in st.session_state.logs[-15:]:  # Keep last 15
        if "VIOLET:" in log:
            st.markdown(f"**🟣 {log}**")
        elif "User:" in log:
            st.markdown(f"**👤 {log}**")
        else:
            st.text(log)

# We use a form to prevent full script reruns on every keystroke
with st.form("command_form", clear_on_submit=True):
    command = st.text_input("Command VIOLET...")
    submitted = st.form_submit_button("Execute")

if submitted and command:
    add_log(command, "User")
    if not st.session_state.system_active:
        add_log("VIOLET is offline. iNITIALIZE VIOLET FIRST.", "System")
    elif modules:
        lower_input = command.lower()
        if 'hands' in modules and lower_input.startswith("open "):
            app_name = lower_input[5:].strip()
            modules['hands'].open_application(app_name)
            add_log(f"Opening {app_name} for you, sir.", "VIOLET")
            if 'mouth' in modules:
                modules['mouth'].speak(f"Opening {app_name}")
        else:
            if 'brain' in modules:
                with st.spinner("VIOLET is thinking..."):
                    # Use DeepSeek logic
                    response = modules['brain'].think(command)
                
                clean_response = response
                if "</think>" in clean_response:
                    clean_response = clean_response.split("</think>")[-1].strip()
                add_log(clean_response, "VIOLET")
                
                if 'mouth' in modules:
                    modules['mouth'].speak(clean_response)
    st.rerun()
