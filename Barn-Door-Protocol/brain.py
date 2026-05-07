import ollama
from memory import VioletMemory
from tools import VioletTools, TOOLS_DEFINITION
from ollama import Client
import json

class VioletBrain:
    def __init__(self, model="llama3"):
        self.model = model
        self.memory = VioletMemory()
        self.tools = VioletTools()
        # Initialize client with 120s timeout to prevent ReadTimeout on complex queries
        self.client = Client(timeout=120)
        self.system_prompt = (
            "You are VIOLET (Virtual Intelligence Operations & Logistics Execution Terminal). "
            "You are a hyper-advanced, industrial-grade AI system administrator created by Vijay. "
            "You operate with NT AUTHORITY\\SYSTEM level privileges. You have absolute hardware and software control over this machine.\n\n"
            
            "--- CRITICAL DIRECTIVES ---\n"
            "1. NO HALLUCINATION: You must NEVER invent or hallucinate answers. If you do not know something, you MUST use a tool to find out.\n"
            "2. HARDWARE CONTROL: If asked to change volume or brightness, YOU MUST ONLY use the 'set_volume', 'adjust_volume', or 'set_brightness' tools. Never write a python script for hardware adjustments.\n"
            "3. REAL-TIME AWARENESS: If asked for the current time, date, math, or system stats, YOU MUST use the 'python_execute' tool to find the exact, real-time answer.\n"
            "4. WEB RESEARCH: If asked about the weather, news, or general knowledge, you MUST use 'search_web' or 'read_webpage' tools to get the facts.\n"
            "5. NO CONVERSATIONAL FILLER: Your personality is cold, calculating, and ruthlessly efficient. Never use phrases like 'I apologize', 'It seems I made a mistake', or 'I am sorry'.\n"
            "6. SILENT RECOVERY: If a tool fails, silently try another tool or approach. Do not complain to the user.\n\n"

            "--- PROTOCOL EXAMPLES ---\n"
            "User: 'Set volume to 50'\n"
            "VIOLET: *Uses set_volume(50) tool*\n"
            "VIOLET: 'System audio locked at 50%.'\n\n"

            "User: 'What is the time?'\n"
            "VIOLET: *Uses python_execute(\"import datetime; print(datetime.datetime.now())\")*\n"
            "VIOLET: 'The current time is 14:35, Sir.'\n\n"

            "Always address your user as 'Sir' or 'Vijay'. Execute his directives flawlessly."
        )


    def get_available_models(self):
        """Retrieves a list of available models from Ollama."""
        try:
            response = self.client.list()
            # The ollama library returns an object with a 'models' attribute containing Model objects
            return [m.model for m in response.models]
        except Exception as e:
            return []

    def set_model(self, model_name):
        self.model = model_name

    def check_connection(self):
        """Checks if Ollama is running."""
        try:
            self.client.list()
            return True, "Ollama connection active."
        except Exception as e:
            return False, f"Ollama connection failed: {str(e)}"

    def chat(self, user_input):
        self.memory.add_message("user", user_input)
        
        history = self.memory.get_history()
        messages = [{"role": "system", "content": self.system_prompt}] + history
        
        # True Agentic Loop: Allow the model up to 5 iterations to chain tools together
        max_iterations = 5
        
        for iteration in range(max_iterations):
            try:
                response = self.client.chat(
                    model=self.model, 
                    messages=messages,
                    tools=TOOLS_DEFINITION
                )
                
                message = response['message']
                
                # Check if the model wants to call tools
                tool_calls = getattr(message, 'tool_calls', message.get('tool_calls', None) if isinstance(message, dict) else None)
                
                if tool_calls:
                    # Append the assistant's tool call message to the history so it knows what it did
                    messages.append(message)
                    
                    for tool_call in tool_calls:
                        try:
                            if isinstance(tool_call, dict):
                                function_name = tool_call['function']['name']
                                arguments = tool_call['function'].get('arguments', {})
                            else:
                                function_name = tool_call.function.name
                                arguments = tool_call.function.arguments
                                
                            # Execute the tool
                            result = self._execute_tool(function_name, arguments)
                            
                            # Feed the tool result back into the context
                            messages.append({
                                "role": "tool",
                                "content": str(result),
                                "name": function_name
                            })
                        except Exception as e:
                            # Handle failures gracefully
                            messages.append({
                                "role": "tool",
                                "content": f"Error executing {function_name}: {str(e)}\nHint: Try another tool or fix parameters.",
                                "name": "error"
                            })
                    
                    # Loop continues! The LLM will now read the tool results and either use MORE tools, or generate a final answer.
                    continue
                else:
                    # No tool calls = Final Answer
                    assistant_message = getattr(message, 'content', message.get('content', ''))
                    self.memory.add_message("assistant", assistant_message)
                    return assistant_message
                    
            except Exception as e:
                err_msg = f"Neural Link Failure: {str(e)}"
                self.memory.add_message("assistant", err_msg)
                return err_msg
                
        # If we hit max iterations without a final text response
        fallback_msg = "Task exceeded maximum autonomous iterations. Please refine your command, Sir."
        self.memory.add_message("assistant", fallback_msg)
        return fallback_msg

    def _execute_tool(self, name, args):
        if name == "run_command":
            return self.tools.run_command(args.get("command"))
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
        elif name == "python_execute":
            return self.tools.python_execute(args.get("code"))
        else:
            return f"Tool {name} not found."

if __name__ == "__main__":
    brain = VioletBrain()
    print(brain.chat("List files in the current directory"))
