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
        """Sets the system volume (0-100) using PowerShell."""
        try:
            # Simple PowerShell command for volume
            command = f"(num = {level} / 100 * 65535); (New-Object -ComObject WScript.Shell).SendKeys([char]174)*50; (New-Object -ComObject WScript.Shell).SendKeys([char]175)*($num/1310)"
            # That one is complex, let's use a simpler one or a library.
            # Actually, using a specialized library like 'pycaw' is better but requires more setup.
            # Let's use the NirCmd if available, or just a simple PS script for mute/unmute and basic steps.
            # For now, let's use a standard PS command to set volume level.
            ps_command = f"$wsh = New-Object -ComObject WScript.Shell; for($i=0; $i -lt 50; $i++) {{ $wsh.SendKeys([char]174) }}; for($i=0; $i -lt {level}/2; $i++) {{ $wsh.SendKeys([char]175) }}"
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
            return f"System volume set to approximately {level}%"
        except Exception as e:
            return f"Error setting volume: {str(e)}"

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
            return f"Searching web for: {query}"
        except Exception as e:
            return f"Error searching web: {str(e)}"

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

# Dictionary of available tools for the LLM to understand
TOOLS_DEFINITION = [
    {
        "name": "run_command",
        "description": "Execute a system/shell command",
        "parameters": {"command": "The command string to run"}
    },
    {
        "name": "python_execute",
        "description": "Write and execute Python code to solve complex tasks (e.g., math, file manipulation, system checks)",
        "parameters": {"code": "The Python code block to execute"}
    },
    {
        "name": "list_files",
        "description": "List files in a directory",
        "parameters": {"path": "The directory path (default is current directory)"}
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {"file_path": "The path to the file"}
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "parameters": {"file_path": "The path to the file", "content": "The content to write"}
    },
    {
        "name": "get_system_metrics",
        "description": "Get current CPU and RAM usage",
        "parameters": {}
    },
    {
        "name": "set_volume",
        "description": "Set system volume (0 to 100)",
        "parameters": {"level": "The volume level from 0 to 100"}
    },
    {
        "name": "open_app",
        "description": "Open a system application",
        "parameters": {"app_name": "The name of the application"}
    }
]
