from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

from brain import VioletBrain
from tools import VioletTools
from voice import VioletVoice

app = FastAPI(title="VIOLET Core")

# Ensure templates directory exists
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

brain = VioletBrain() # Will default to best model or require setup
tools = VioletTools()
voice = VioletVoice()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    # Auto-select the first available model for the web interface
    models = brain.get_available_models()
    if models:
        brain.set_model(models[0])
        model_name = models[0]
    else:
        model_name = "No Model Detected"
        
    return templates.TemplateResponse(request=request, name="index.html", context={"model_name": model_name, "available_models": models})

@app.post("/set_model")
async def set_model_endpoint(model_name: str = Form(...)):
    try:
        models = brain.get_available_models()
        if model_name in models:
            brain.set_model(model_name)
            return {"status": "success", "message": f"Engine switched to {model_name}"}
        else:
            return {"status": "error", "message": "Model not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/chat")
def chat_endpoint(message: str = Form(...)):
    try:
        final_response = ""
        for chunk in brain.chat(message):
            if not chunk.startswith("SYSTEM:"):
                final_response = chunk
                
        # Voice is non-blocking now
        voice.speak(final_response)
        return {"status": "success", "response": final_response}
    except Exception as e:
        return {"status": "error", "response": str(e)}

@app.get("/status")
def get_status():
    try:
        metrics = tools.get_system_metrics().split("\n")
        cpu = metrics[0].split(": ")[1]
        ram = metrics[1].split(": ")[1]
        return {"cpu": cpu, "ram": ram}
    except:
        return {"cpu": "N/A", "ram": "N/A"}

if __name__ == "__main__":
    print("Starting VIOLET Dynamic Web Server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
