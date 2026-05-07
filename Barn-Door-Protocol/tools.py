import os
import subprocess
import shutil

class VioletTools:
    @staticmethod
    def run_command(command):
        """Executes a system command safely with a timeout and returns the output."""
        try:
            # Added a 15-second timeout to prevent system lockups from hanging commands
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
            output = f"STDOUT: {result.stdout}"
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            return output.strip() or "Command executed successfully (no output)."
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 15 seconds. It may be trapped in a loop or waiting for input."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @staticmethod
    def list_files(path="."):
        """Lists files and directories in a given path."""
        try:
            items = os.listdir(path)
            return "\n".join(items)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    @staticmethod
    def read_file(file_path):
        """Reads the content of a file."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def write_file(file_path, content):
        """Writes content to a file."""
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    @staticmethod
    def get_system_metrics():
        """Returns current CPU and RAM usage."""
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        return f"CPU Usage: {cpu}%\nRAM Usage: {ram}%"

    @staticmethod
    def list_processes():
        """Lists the top 10 most memory-intensive processes."""
        import psutil
        processes = sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), 
                           key=lambda x: x.info['memory_percent'], reverse=True)[:10]
        return "\n".join([f"PID: {p.info['pid']} | Name: {p.info['name']} | RAM: {p.info['memory_percent']:.2f}%" for p in processes])

    @staticmethod
    def get_cwd():
        """Returns the current working directory."""
        return os.getcwd()

    @staticmethod
    def change_dir(path):
        """Changes the current working directory."""
        try:
            os.chdir(path)
            return f"Changed directory to {os.getcwd()}"
        except Exception as e:
            return f"Error changing directory: {str(e)}"

    @staticmethod
    def set_volume(level):
        """Sets the system volume (0-100) using Pycaw for industrial-grade accuracy."""
        try:
            from pycaw.pycaw import AudioUtilities
            
            # Use the modern pycaw API
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            
            # Convert 0-100 scalar to dB using Pycaw's SetMasterVolumeLevelScalar
            scalar_level = max(0.0, min(100.0, float(level))) / 100.0
            volume.SetMasterVolumeLevelScalar(scalar_level, None)
            
            return f"System audio output locked at {level}%"
        except Exception as e:
            return f"Hardware interface error (Audio): {str(e)}"

    @staticmethod
    def adjust_volume(direction):
        """Adjusts the system volume up or down by 10%."""
        try:
            from pycaw.pycaw import AudioUtilities
            
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            
            current_scalar = volume.GetMasterVolumeLevelScalar()
            if direction.lower() == "up":
                new_scalar = min(1.0, current_scalar + 0.10)
            elif direction.lower() == "down":
                new_scalar = max(0.0, current_scalar - 0.10)
            else:
                return "Direction must be 'up' or 'down'."
                
            volume.SetMasterVolumeLevelScalar(new_scalar, None)
            return f"Volume adjusted {direction}."
        except Exception as e:
            return f"Hardware interface error (Audio): {str(e)}"

    @staticmethod
    def set_brightness(level):
        """Sets the system display brightness (0-100)."""
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            return f"Display brightness calibrated to {level}%"
        except Exception as e:
            return f"Hardware interface error (Display): {str(e)}"

    @staticmethod
    def open_app(app_name):
        """Opens an application by name."""
        try:
            # Common apps mapping
            apps = {
                "edge": "msedge",
                "chrome": "chrome",
                "notepad": "notepad",
                "calculator": "calc",
                "explorer": "explorer"
            }
            cmd = apps.get(app_name.lower(), app_name)
            subprocess.Popen(cmd, shell=True)
            return f"Attempting to open {app_name}..."
        except Exception as e:
            return f"Error opening app: {str(e)}"

    @staticmethod
    def search_web(query):
        """Searches the web using the default browser."""
        import webbrowser
        try:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return f"Opened browser to search for: {query}"
        except Exception as e:
            return f"Error searching web: {str(e)}"

    @staticmethod
    def read_webpage(url):
        """Fetches and extracts text content from a webpage."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text from paragraphs
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if not text:
                text = soup.get_text(separator=' ', strip=True)
                
            # Limit return size to prevent context overflow
            return text[:2000] + ("..." if len(text) > 2000 else "")
        except Exception as e:
            return f"Error reading webpage {url}: {str(e)}"

    @staticmethod
    def python_execute(code):
        """Executes arbitrary Python code safely with a timeout and captures output."""
        import tempfile
        import subprocess
        import os
        
        # Write code to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(code)
            
        try:
            # Execute the temp file in a subprocess with a 15-second timeout
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
                
            return output.strip() or "Code executed successfully (no output)."
            
        except subprocess.TimeoutExpired:
            return "Error: Python execution timed out after 15 seconds. Possible infinite loop."
        except Exception as e:
            return f"Error executing Python code: {str(e)}"
        finally:
            # Clean up the temp file
            try:
                os.remove(temp_path)
            except:
                pass

# Dictionary of available tools formatted exactly for Ollama JSON Schema Function Calling
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a system/shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command string to run"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "python_execute",
            "description": "Write and execute Python code to solve complex tasks (e.g., math, file manipulation, system checks)",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The Python code block to execute"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The directory path (default is current directory)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "The path to the file"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "The path to the file"},
                    "content": {"type": "string", "description": "The content to write"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_metrics",
            "description": "Get current CPU and RAM usage",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set system volume exactly to a specific percentage (0 to 100)",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "The volume level from 0 to 100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adjust_volume",
            "description": "Turn the system volume 'up' or 'down' relative to its current state",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "description": "Must be 'up' or 'down'"}
                },
                "required": ["direction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Set system display brightness exactly to a specific percentage (0 to 100)",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "The brightness level from 0 to 100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a system application",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "The name of the application"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Open a browser to search google for a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": "Fetch and read the text content of a URL from the internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full URL of the webpage to read"}
                },
                "required": ["url"]
            }
        }
    }
]
