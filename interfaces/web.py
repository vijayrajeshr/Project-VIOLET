import os
import sys
import tempfile
import asyncio
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.brain import VioletBrain
from core.ears import VioletEars
from core.mouth import VioletMouth
from core.tools import VioletTools

app = FastAPI(title="VIOLET System Dashboard")

# Ensure templates folder exists
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# Initialize core modules
brain = VioletBrain(backend=os.getenv("LLM_BACKEND", "ollama"))
ears = VioletEars(provider=os.getenv("STT_PROVIDER", "google"))
mouth = VioletMouth(enabled=(os.getenv("TTS_ENABLED", "true").lower() == "true"))
tools = VioletTools()

# Keep track of active console logs to stream to UI
console_logs = ["VIOLET system core initialized.", "Neural links active."]

def add_console_log(msg):
    import time
    timestamp = time.strftime("%H:%M:%S")
    console_logs.append(f"[{timestamp}] {msg}")
    if len(console_logs) > 40:
        console_logs.pop(0)

@app.get("/", response_class=HTMLResponse)
def index_route(request: Request):
    models = brain.get_available_models()
    active_model = brain.model
    backend = brain.backend
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "available_models": models,
            "active_model": active_model,
            "backend": backend,
            "stt_provider": ears.provider,
            "tts_enabled": mouth.enabled
        }
    )

@app.get("/status")
def status_endpoint():
    """Returns live telemetry data for gauges."""
    metrics = tools.get_system_metrics().split("\n")
    cpu = metrics[0].split(": ")[1].replace("%", "") if len(metrics) > 0 else "0"
    ram = metrics[1].split(": ")[1].replace("%", "") if len(metrics) > 1 else "0"
    cwd = tools.get_cwd()
    return {
        "cpu": cpu,
        "ram": ram,
        "cwd": cwd,
        "model": brain.model,
        "backend": brain.backend,
        "logs": console_logs
    }

@app.post("/set_config")
def config_endpoint(
    model_name: str = Form(None), 
    backend: str = Form(None), 
    stt_provider: str = Form(None),
    tts_enabled: str = Form(None)
):
    try:
        if backend:
            brain.backend = backend.lower().strip()
            add_console_log(f"Switched backend adapter to: {backend}")
        if model_name:
            brain.model = model_name.strip()
            add_console_log(f"Switched active AI engine to: {model_name}")
        if stt_provider:
            ears.provider = stt_provider.lower().strip()
            if ears.provider == "whisper":
                ears.load_whisper_model()
            add_console_log(f"Switched speech recognition provider to: {stt_provider}")
        if tts_enabled is not None:
            mouth.enabled = (tts_enabled.lower() == "true")
            add_console_log(f"VIOLET voice synthesizer: {'ENABLED' if mouth.enabled else 'DISABLED'}")
        
        return {"status": "success", "message": "Configuration updated successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/transcribe")
async def transcribe_endpoint(audio: UploadFile = File(...)):
    """Receives WAV file from web client, transcribes it, and returns the text."""
    try:
        # Write binary stream to a temporary WAV file
        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        with open(temp_path, "wb") as f:
            f.write(await audio.read())
            
        add_console_log("Received audio chunk. Transcribing...")
        text = ears.transcribe_file(temp_path)
        
        # Clean up
        try:
            os.remove(temp_path)
        except:
            pass
            
        add_console_log(f"Transcription result: '{text}'")
        return {"status": "success", "text": text}
    except Exception as e:
        add_console_log(f"Transcription error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/execute_tool")
def execute_tool_endpoint(tool_name: str = Form(...), params: str = Form(...)):
    """Allows direct execution of system tools from the dashboard widgets."""
    try:
        add_console_log(f"Direct UI trigger: executing tool {tool_name} with params '{params}'")
        parsed_params = json.loads(params) if params else {}
        result = brain._execute_tool(tool_name, parsed_params)
        add_console_log(f"Tool {tool_name} output: {result}")
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/chat_stream")
def chat_stream_endpoint(message: str):
    """Server-Sent Events (SSE) streaming chat endpoint."""
    add_console_log(f"Query: '{message}'")
    
    async def sse_generator():
        loop = asyncio.get_event_loop()
        # Define a synchronous runner for generator
        def run_chat():
            return list(brain.chat(message))
            
        try:
            # Run the chat generator in executor thread to prevent blocking asyncio loop
            responses = await loop.run_in_executor(None, run_chat)
            
            for chunk in responses:
                if chunk.startswith("SYSTEM:"):
                    # Yield tool/system execution updates
                    add_console_log(chunk)
                    yield f"event: system\ndata: {chunk}\n\n"
                else:
                    # Yield final answer text
                    add_console_log("VIOLET generated response.")
                    # Speak response in background thread
                    mouth.speak(chunk)
                    # Escape newlines for SSE transport
                    safe_chunk = chunk.replace("\n", "\\n")
                    yield f"event: message\ndata: {safe_chunk}\n\n"
                    
        except Exception as e:
            err = f"SSE Stream Error: {str(e)}"
            add_console_log(err)
            yield f"event: error\ndata: {err}\n\n"
            
    return StreamingResponse(sse_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv()
    print("Starting VIOLET FastAPI server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
