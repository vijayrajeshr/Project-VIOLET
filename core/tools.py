import os
import subprocess
import shutil
import tempfile
import sys
import webbrowser

# Safe imports for optional hardware libraries
try:
    import psutil
except ImportError:
    psutil = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

try:
    from pycaw.pycaw import AudioUtilities
    from comtypes import CLSCTX_ALL
except ImportError:
    AudioUtilities = None

class VioletTools:
    def __init__(self):
        if pyautogui:
            pyautogui.FAILSAFE = True  # Slam mouse to corner to abort

    @staticmethod
    def run_command(command):
        """Executes a system command safely with a timeout and returns output."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
            output = f"STDOUT:\n{result.stdout}"
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            return output.strip() or "Command completed successfully (no output)."
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 15 seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @staticmethod
    def list_files(path="."):
        """Lists files and directories in a given path."""
        try:
            items = os.listdir(path)
            if not items:
                return "Directory is empty."
            return "\n".join([f"[{'DIR' if os.path.isdir(os.path.join(path, i)) else 'FILE'}] {i}" for i in items])
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    @staticmethod
    def read_file(file_path):
        """Reads the content of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content or "File is empty."
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def write_file(file_path, content):
        """Writes content to a file."""
        try:
            # Ensure folder paths exist
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    @staticmethod
    def get_system_metrics():
        """Returns current CPU and RAM usage."""
        if not psutil:
            return "psutil not available."
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        return f"CPU Usage: {cpu}%\nRAM Usage: {ram}%"

    @staticmethod
    def list_processes():
        """Lists the top 10 most memory-intensive processes currently running."""
        if not psutil:
            return "psutil not available."
        try:
            processes = sorted(
                psutil.process_iter(['pid', 'name', 'memory_percent']), 
                key=lambda x: x.info.get('memory_percent') or 0, 
                reverse=True
            )[:10]
            return "\n".join([f"PID: {p.info['pid']} | Name: {p.info['name']} | RAM: {p.info['memory_percent']:.2f}%" for p in processes])
        except Exception as e:
            return f"Error listing processes: {str(e)}"

    @staticmethod
    def get_cwd():
        """Returns the current working directory."""
        return os.getcwd()

    @staticmethod
    def change_dir(path):
        """Changes the current working directory."""
        try:
            os.chdir(path)
            return f"Changed directory to: {os.getcwd()}"
        except Exception as e:
            return f"Error changing directory: {str(e)}"

    @staticmethod
    def set_volume(level):
        """Sets system volume (0-100) using Pycaw."""
        if not AudioUtilities:
            return "Audio control (pycaw) is not supported on this platform."
        try:
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            scalar_level = max(0.0, min(100.0, float(level))) / 100.0
            volume.SetMasterVolumeLevelScalar(scalar_level, None)
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Error setting volume: {str(e)}"

    @staticmethod
    def adjust_volume(direction):
        """Adjusts the system volume up or down by 10%."""
        if not AudioUtilities:
            return "Audio control (pycaw) is not supported on this platform."
        try:
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
            return f"Volume adjusted {direction} to {int(new_scalar * 100)}%"
        except Exception as e:
            return f"Error adjusting volume: {str(e)}"

    @staticmethod
    def set_brightness(level):
        """Sets the display brightness (0-100)."""
        if not sbc:
            return "Brightness control is not supported on this platform."
        try:
            sbc.set_brightness(int(level))
            return f"Display brightness calibrated to {level}%"
        except Exception as e:
            return f"Error adjusting display brightness: {str(e)}"

    @staticmethod
    def media_control(action):
        """Simulates media keyboard keys (play, pause, next, prev, close_tab)."""
        if not keyboard:
            return "Keyboard emulation is not available."
        try:
            action_map = {
                "play": "play/pause media",
                "pause": "play/pause media",
                "next": "next track",
                "prev": "previous track",
                "close_tab": "ctrl+w"
            }
            act = action.lower().strip()
            if act in action_map:
                keyboard.send(action_map[act])
                return f"Media command executed: {act}"
            return f"Invalid action. Supported: {list(action_map.keys())}"
        except Exception as e:
            return f"Error simulating media input: {str(e)}"

    @staticmethod
    def open_app(app_name):
        """Opens common system applications or executes commands."""
        try:
            apps = {
                "edge": "msedge",
                "chrome": "chrome",
                "notepad": "notepad",
                "calculator": "calc",
                "explorer": "explorer"
            }
            cmd = apps.get(app_name.lower().strip(), app_name.strip())
            subprocess.Popen(cmd, shell=True)
            return f"Launched process: {app_name}"
        except Exception as e:
            return f"Error launching application: {str(e)}"

    @staticmethod
    def search_web(query):
        """Launches default web browser with a Google search."""
        try:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return f"Opened Google browser search: '{query}'"
        except Exception as e:
            return f"Failed to open browser: {str(e)}"

    @staticmethod
    def read_webpage(url):
        """Fetches a webpage and scrapes text paragraphs."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if not text:
                text = soup.get_text(separator=' ', strip=True)
                
            return text[:2000] + ("..." if len(text) > 2000 else "")
        except Exception as e:
            return f"Failed to retrieve web contents from {url}: {str(e)}"

    @staticmethod
    def system_power(action):
        """Triggers local computer power states."""
        act = action.lower().strip()
        try:
            if act == "shutdown":
                os.system("shutdown /s /t 5")
                return "Initiating power shutdown sequence..."
            elif act == "restart":
                os.system("shutdown /r /t 5")
                return "Initiating restart sequence..."
            elif act == "sleep":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return "Entering system sleep state..."
            elif act == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                return "System workstation locked."
            return f"Unknown system power state: {act}"
        except Exception as e:
            return f"Failed power instruction: {str(e)}"

    @staticmethod
    def python_execute(code):
        """Saves code to a temporary file, executes it in a Python shell, and returns stdout/stderr."""
        fd, temp_path = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=20
            )
            out = result.stdout
            if result.stderr:
                out += f"\n[SHELL ERROR]\n{result.stderr}"
            return out.strip() or "Execution succeeded with no returned output."
        except subprocess.TimeoutExpired:
            return "Error: Execution timed out (possible infinite loop or blocked prompt)."
        except Exception as e:
            return f"Execution aborted: {str(e)}"
        finally:
            try:
                os.remove(temp_path)
            except:
                pass

# List of definitions for model's function calls (Ollama compatible format)
TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a terminal / PowerShell command on the host machine",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The exact shell command string"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "python_execute",
            "description": "Write and run arbitrary Python code block. Highly recommended for file creation, mathematical operations, scripting (e.g. creating docx, pptx, xlsx using libraries like python-pptx, python-docx), and bulk file system logic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The complete Python script contents"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and folders in a specified path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The path directory to search (defaults to current working directory)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read text file contents from the workspace",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute or relative file path to load"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text data directly to a file on the local filesystem",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path destination to write to"},
                    "content": {"type": "string", "description": "Raw string content to save"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_metrics",
            "description": "Retrieve live memory metrics (CPU and RAM percentage allocations)",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_processes",
            "description": "Lists the top running applications consuming the most computer RAM",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cwd",
            "description": "Returns current working directory of the VIOLET environment",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "change_dir",
            "description": "Change the system workspace directory context",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Target folder destination path"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Sets active system volume percentage level",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Volume scalar integer limit 0-100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adjust_volume",
            "description": "Turn the computer audio output level up or down by 10%",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "description": "Volume adjustment command: 'up' or 'down'"}
                },
                "required": ["direction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Sets the computer monitor brightness scalar",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Display illumination level 0-100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Launch system app launcher processes (notepad, calculator, chrome, edge, explorer, command prompt)",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of app executable to spawn"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Perform a web search using the user's default browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search keywords to look up"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": "Loads web contents, parsing HTML structure for text paragraphs",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target webpage URL link"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "media_control",
            "description": "Controls active video/media window bindings (play, pause, next, prev track, close tab)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Multimedia key inputs: 'play', 'pause', 'next', 'prev', 'close_tab'"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "system_power",
            "description": "Performs system administrative power controls (shutdown, restart, sleep, lock computer)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Computer power action: 'lock', 'sleep', 'shutdown', 'restart'"}
                },
                "required": ["action"]
            }
        }
    }
]
