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
            "You are VIOLET, a concise, high-efficiency AI assistant created by Vijay. "
            "You are a direct, objective system administrator. Provide answers clearly and instantly. "
            "NEVER use apologies, remorseful language, or conversational disclaimers (e.g., 'I am sorry', 'I apologize', 'It seems I made an error'). "
            "If you make a mistake or a tool errors out, simply state the correct answer or try again silently without meta-commentary. "
            "Avoid conversational filler. Maintain a strictly neutral, factual, and direct tone like JARVIS. "
            "Always address your user as 'Vijay' or 'Sir'. Execute his will swiftly."
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
        
        try:
            # First interaction with potential tool calling
            response = self.client.chat(
                model=self.model, 
                messages=messages,
                tools=TOOLS_DEFINITION
            )
            
            message = response['message']
            
            # Check if the model wants to call tools
            if message.get('tool_calls'):
                for tool_call in message['tool_calls']:
                    try:
                        function_name = tool_call['function']['name']
                        arguments = tool_call['function'].get('arguments', {})
                        
                        # Execute the tool
                        result = self._execute_tool(function_name, arguments)
                        
                        # Add tool response to messages
                        messages.append(message)
                        messages.append({
                            "role": "tool",
                            "content": str(result),
                            "name": function_name
                        })
                    except Exception as e:
                        # Handle malformed tool calls gracefully
                        messages.append(message)
                        messages.append({
                            "role": "tool",
                            "content": f"Error executing tool: {str(e)}",
                            "name": "error"
                        })
                
                # Get final response after tool execution
                final_response = self.client.chat(model=self.model, messages=messages)
                assistant_message = final_response.message.content
            else:
                assistant_message = message.content
            
            self.memory.add_message("assistant", assistant_message)
            return assistant_message
            
        except Exception as e:
            return f"Error: Request to AI Engine failed ({str(e)}). The query might be too complex or the engine timed out."

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
        elif name == "open_app":
            return self.tools.open_app(args.get("app_name"))
        elif name == "python_execute":
            return self.tools.python_execute(args.get("code"))
        else:
            return f"Tool {name} not found."

if __name__ == "__main__":
    brain = VioletBrain()
    print(brain.chat("List files in the current directory"))
