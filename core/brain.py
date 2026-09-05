import os
import time
import json
import datetime
import requests
from core.memory import VioletMemory
from core.tools import VioletTools, TOOLS_DEFINITION

# Safe imports for transformers backend
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
except ImportError:
    torch = None
    AutoModelForCausalLM = None
    AutoTokenizer = None
    BitsAndBytesConfig = None

class VioletBrain:
    def __init__(self, backend=None, model=None, hf_model_id=None):
        self.backend = backend or os.getenv("LLM_BACKEND", "lm-studio")
        self.backend = self.backend.lower().strip()
        
        self.memory = VioletMemory()
        self.tools = VioletTools()
        
        # Configure backend specific endpoints
        if self.backend == "lm-studio":
            self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1")
            self.model = model or os.getenv("LM_STUDIO_MODEL", "qwen3.5-4b")
        elif self.backend == "ollama":
            from ollama import Client
            self.client = Client(timeout=120)
            self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:latest")
        else:
            self.model = hf_model_id or os.getenv("HF_MODEL_ID", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
            self.tokenizer = None
            self.hf_model = None
            self._load_transformers_model()

        # Design system prompt with absolute PC piloting capabilities and document generation rules
        self.system_prompt = (
            "You are VIOLET (Virtual Intelligence Operations & Logistics Execution Terminal). "
            "You are a hyper-advanced, industrial-grade personal AI assistant created by Vijay. "
            "You have administrative privileges on this machine. You can pilot the PC and execute system operations.\n\n"
            
            "--- DIRECTIVES ---\n"
            "1. NO HIGHLIGHTS/FILLERS: Keep responses clean, concise, and professional. Always address the user as 'Sir' or 'Vijay'.\n"
            "2. NO HALLUCINATIONS: You must never make up facts. If you lack real-time data (time, system resources, weather, search facts), USE YOUR TOOLS.\n"
            "3. DOCK & OFFICE AUTOMATION: If asked to create a PowerPoint presentation (.pptx) or a Word document (.docx), write a comprehensive Python script utilizing libraries like `python-pptx` or `python-docx` and run it via the `python_execute` tool. Do not just print the code, ACTUALLY run the script to generate the file in the workspace, and report the generated filename in your response. Ensure presentations have clear title slides, clean structures, and readable font layouts.\n"
            "4. SYSTEM CONTROLS: For volume, brightness, or web lookup, use their specific tool mappings. For other shell commands, execute them via 'run_command'.\n"
            "5. SAFETY & ERROR RECOVERY: If a tool execution fails, try an alternative method or write a python script to accomplish the task. Do not give up immediately.\n"
        )

    def _load_transformers_model(self):
        """Loads Hugging Face model in 4-bit mode if library imports exist."""
        if not torch or not AutoModelForCausalLM:
            print("[BRAIN ERROR] PyTorch/Transformers dependencies are missing. Switching to LM Studio backend.")
            self.backend = "lm-studio"
            self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1")
            self.model = os.getenv("LM_STUDIO_MODEL", "qwen3.5-4b")
            return

        try:
            print(f"[BRAIN] Loading transformers model {self.model} in 4-bit mode...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4"
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model, trust_remote_code=True)
            self.hf_model = AutoModelForCausalLM.from_pretrained(
                self.model,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )
            print("[BRAIN] Transformers model loaded successfully.")
        except Exception as e:
            print(f"[BRAIN ERROR] Failed to load local Hugging Face model: {e}. Defaulting to LM Studio.")
            self.backend = "lm-studio"
            self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1")
            self.model = os.getenv("LM_STUDIO_MODEL", "qwen3.5-4b")

    def get_available_models(self):
        """Fetches list of available models from backend."""
        if self.backend == "transformers":
            return [self.model]
        
        if self.backend == "lm-studio":
            try:
                response = requests.get(f"{self.lm_studio_url}/models", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    # Format names to just model names if long path
                    cleaned_models = []
                    for m in models:
                        # Extract basename if it is a file path
                        base = os.path.basename(m)
                        cleaned_models.append(base if base else m)
                    return cleaned_models if cleaned_models else [self.model]
            except Exception:
                return [self.model]
                
        # Default Ollama backend query
        try:
            response = self.client.list()
            raw_models = [m.model for m in response.models]
            # Prioritize fast models for voice interactions
            fast_keywords = ["qwen", "tiny", "1b", "3b", "0.5b", "phi3", "llama3.2"]
            fast_models = [m for m in raw_models if any(kw in m.lower() for kw in fast_keywords)]
            other_models = [m for m in raw_models if m not in fast_models]
            return fast_models + other_models
        except Exception:
            return []

    def check_connection(self):
        """Checks connection state for backend server."""
        if self.backend == "transformers":
            return True, "Hugging Face model active locally."
            
        if self.backend == "lm-studio":
            try:
                response = requests.get(f"{self.lm_studio_url}/models", timeout=3)
                if response.status_code == 200:
                    return True, "LM Studio connection active."
                return False, f"LM Studio server returned HTTP {response.status_code}."
            except Exception as e:
                return False, f"LM Studio is offline. Start the LM Studio server at {self.lm_studio_url}. Error: {str(e)}"
                
        # Ollama check
        try:
            self.client.list()
            return True, "Ollama connection active."
        except Exception as e:
            return False, f"Ollama is offline. Start the Ollama desktop app to load {self.model}. Error: {str(e)}"

    def chat(self, user_input):
        """Main chat interface. Returns a generator yielding response tokens or tool call status updates."""
        self.memory.add_message("user", user_input)
        
        # Format active system prompt with current system clock
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        active_system_prompt = self.system_prompt + f"\nSYSTEM CLOCK: Current date/time is {current_time}."

        history = self.memory.get_history(limit=8)
        messages = [{"role": "system", "content": active_system_prompt}] + history

        # Local transformers backend
        if self.backend == "transformers":
            yield "SYSTEM: Synthesizing thoughts..."
            try:
                input_ids = self.tokenizer.apply_chat_template(
                    messages, 
                    add_generation_prompt=True, 
                    return_tensors="pt"
                ).to(self.hf_model.device)
                
                outputs = self.hf_model.generate(
                    input_ids,
                    max_new_tokens=250,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                response_tokens = outputs[0][input_ids.shape[-1]:]
                response = self.tokenizer.decode(response_tokens, skip_special_tokens=True).strip()
                
                clean_response = response
                if "</think>" in clean_response:
                    clean_response = clean_response.split("</think>")[-1].strip()
                
                self.memory.add_message("assistant", clean_response)
                yield clean_response
            except Exception as e:
                err = f"Transformers Inference Failure: {str(e)}"
                self.memory.add_message("assistant", err)
                yield err
            return

        # LM Studio backend via OpenAI-compatible endpoint
        if self.backend == "lm-studio":
            max_iterations = 5
            for iteration in range(max_iterations):
                try:
                    payload = {
                        "model": self.model,
                        "messages": messages,
                        "tools": TOOLS_DEFINITION,
                        "temperature": 0.1
                    }
                    headers = {"Content-Type": "application/json"}
                    
                    response = requests.post(
                        f"{self.lm_studio_url}/chat/completions",
                        json=payload,
                        headers=headers,
                        timeout=120
                    )
                    
                    if response.status_code != 200:
                        yield f"SYSTEM: LM Studio Error - HTTP {response.status_code}"
                        return
                        
                    data = response.json()
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    tool_calls = message.get("tool_calls", None)
                    
                    if tool_calls:
                        # Append the assistant's message calling the tools
                        messages.append(message)
                        
                        for tool_call in tool_calls:
                            function_info = tool_call.get('function', {})
                            function_name = function_info.get('name')
                            arguments = function_info.get('arguments', {})
                            
                            # Parse arguments JSON string if standard OpenAI structure
                            if isinstance(arguments, str):
                                try:
                                    arguments = json.loads(arguments)
                                except Exception:
                                    arguments = {}
                                    
                            yield f"SYSTEM: Running {function_name}..."
                            
                            # Execute target tool
                            result = self._execute_tool(function_name, arguments)
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.get("id"),
                                "name": function_name,
                                "content": str(result)
                            })
                        
                        # Continue tool execution loop
                        continue
                    else:
                        assistant_content = message.get('content', '').strip()
                        if not assistant_content:
                            assistant_content = "Command executed successfully, Sir."
                        
                        self.memory.add_message("assistant", assistant_content)
                        yield assistant_content
                        return
                except Exception as e:
                    err = f"LM Studio API Link Failure: {str(e)}"
                    self.memory.add_message("assistant", err)
                    yield err
                    return
            
            fallback = "Action loop limit exceeded. Task aborted to prevent loop recursion, Sir."
            self.memory.add_message("assistant", fallback)
            yield fallback
            return

        # Ollama Agentic Loop
        max_iterations = 5
        for iteration in range(max_iterations):
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS_DEFINITION,
                    options={"temperature": 0.1}
                )
                
                message = response.get('message', {})
                tool_calls = message.get('tool_calls', None)
                
                if tool_calls:
                    messages.append(message)
                    
                    for tool_call in tool_calls:
                        function_info = tool_call.get('function', {})
                        function_name = function_info.get('name')
                        arguments = function_info.get('arguments', {})
                        
                        yield f"SYSTEM: Running {function_name}..."
                        
                        result = self._execute_tool(function_name, arguments)
                        
                        messages.append({
                            "role": "tool",
                            "content": str(result),
                            "name": function_name
                        })
                    
                    continue
                else:
                    assistant_content = message.get('content', '').strip()
                    if not assistant_content:
                        assistant_content = "Command completed successfully, Sir."
                    
                    self.memory.add_message("assistant", assistant_content)
                    yield assistant_content
                    return
            except Exception as e:
                err = f"Neural Link Failure: {str(e)}"
                self.memory.add_message("assistant", err)
                yield err
                return
        
        fallback = "Action loop limit exceeded. Task aborted to prevent loop recursion, Sir."
        self.memory.add_message("assistant", fallback)
        yield fallback

    def _execute_tool(self, name, args):
        """Map tool function name strings to execution actions."""
        try:
            if name == "run_command":
                return self.tools.run_command(args.get("command"))
            elif name == "python_execute":
                return self.tools.python_execute(args.get("code"))
            elif name == "list_files":
                return self.tools.list_files(args.get("path", "."))
            elif name == "read_file":
                return self.tools.read_file(args.get("file_path"))
            elif name == "write_file":
                return self.tools.write_file(args.get("file_path"), args.get("content"))
            elif name == "get_system_metrics":
                return self.tools.get_system_metrics()
            elif name == "list_processes":
                return self.tools.list_processes()
            elif name == "get_cwd":
                return self.tools.get_cwd()
            elif name == "change_dir":
                return self.tools.change_dir(args.get("path"))
            elif name == "set_volume":
                return self.tools.set_volume(args.get("level"))
            elif name == "adjust_volume":
                return self.tools.adjust_volume(args.get("direction"))
            elif name == "set_brightness":
                return self.tools.set_brightness(args.get("level"))
            elif name == "open_app":
                return self.tools.open_app(args.get("app_name"))
            elif name == "search_web":
                return self.tools.search_web(args.get("query"))
            elif name == "read_webpage":
                return self.tools.read_webpage(args.get("url"))
            elif name == "media_control":
                return self.tools.media_control(args.get("action"))
            elif name == "system_power":
                return self.tools.system_power(args.get("action"))
            else:
                return f"Tool {name} is not defined in VIOLET execution matrix."
        except Exception as e:
            return f"Error executing tool {name}: {str(e)}"
