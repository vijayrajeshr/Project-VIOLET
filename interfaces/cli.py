import os
import sys
import time
import hashlib
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner
from rich.table import Table
from rich.prompt import Prompt

# Add root folder to sys.path so we can import from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.brain import VioletBrain
from core.ears import VioletEars
from core.mouth import VioletMouth
from core.tools import VioletTools

class VioletCLI:
    def __init__(self, admin_hash=None):
        self.console = Console()
        self.admin_hash = admin_hash or os.getenv(
            "ADMIN_HASH", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
        )
        
        # Load core systems
        self.brain = VioletBrain(backend=os.getenv("LLM_BACKEND", "ollama"))
        self.ears = VioletEars(provider=os.getenv("STT_PROVIDER", "google"))
        self.mouth = VioletMouth(enabled=(os.getenv("TTS_ENABLED", "true").lower() == "true"))
        self.tools = VioletTools()
        
        self.voice_requested = False
        self.is_muted = not self.mouth.enabled

    def welcome_screen(self):
        """Displays locked system authenticate page."""
        self.console.clear()
        self.console.print(Panel(
            Text("VIOLET SECURE TERMINAL v3.0", style="bold magenta", justify="center"),
            subtitle="Advanced Agentic AI System Administrator",
            border_style="cyan",
            expand=True
        ))
        
        self.console.print("\n[bold red]AUTHENTICATION REQUIRED[/]")
        attempts = 3
        while attempts > 0:
            pwd = Prompt.ask("[bold yellow]Enter Authorization Code[/]", password=True)
            hashed_pwd = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
            if hashed_pwd == self.admin_hash:
                self.console.print("[bold green]Access Granted. Welcome back, Vijay.[/]\n")
                self.mouth.speak("Access Granted. Welcome back, Vijay.")
                time.sleep(1)
                break
            else:
                attempts -= 1
                self.console.print(f"[bold red]Access Denied.[/] {attempts} attempts remaining.")
                
        if attempts == 0:
            self.console.print("[bold red]Security Lockout. Terminal terminated.[/]")
            sys.exit(1)

        # Connection verify status
        connected, msg = self.brain.check_connection()
        with self.console.status("[bold cyan]Pinging local AI matrix...", spinner="dots"):
            time.sleep(1.5)
        
        if connected:
            self.console.print(f"[bold green]OK:[/] {msg}")
            models = self.brain.get_available_models()
            if models:
                self.console.print(f"[bold green]Active Engine:[/] {self.brain.model}")
        else:
            self.console.print(f"[bold red]ERROR:[/] {msg}")
            if self.brain.backend == "lm-studio":
                self.console.print("[yellow]Please make sure LM Studio server is running at http://127.0.0.1:1234.[/]")
            elif self.brain.backend == "ollama":
                self.console.print("[yellow]Please make sure Ollama is running and download the model first.[/]")
            sys.exit(1)

    def get_status_panel(self):
        """Builds telemetry board table panel."""
        metrics = self.tools.get_system_metrics().split("\n")
        cpu_val = metrics[0].split(": ")[1] if len(metrics) > 0 else "N/A"
        ram_val = metrics[1].split(": ")[1] if len(metrics) > 1 else "N/A"
        cwd = self.tools.get_cwd()
        
        table = Table(show_header=False, border_style="dim")
        table.add_row("CPU Allocation", f"[magenta]{cpu_val}[/]")
        table.add_row("RAM Allocation", f"[magenta]{ram_val}[/]")
        table.add_row("Active CWD", f"[dim]{cwd}[/]")
        table.add_row("Voice Feed", "[red]MUTED (Offline)[/]" if self.is_muted else "[green]ACTIVE (Online)[/]")
        
        return Panel(table, title="[bold white]Telemetry Monitor[/]", border_style="blue")

    def run(self):
        self.welcome_screen()
        
        # Register global keyboard hotkeys if run with admin elevation
        try:
            import keyboard
            def trigger_voice():
                self.voice_requested = True
                keyboard.send('enter') # Break blocking input
            
            keyboard.add_hotkey('ctrl+space', trigger_voice)
            keyboard.add_hotkey('ctrl+m', self.toggle_mute)
            self.console.print("[dim]Hint: Hold 'Ctrl+Space' to record voice. Press 'Ctrl+M' to toggle speaker mute.[/]")
        except Exception:
            self.console.print("[yellow]Warning: Key listener hotkeys disabled. Run CLI terminal as Administrator to enable.[/]")

        while True:
            try:
                self.console.print(self.get_status_panel())
                
                if self.voice_requested:
                    user_input = "/v"
                    self.voice_requested = False
                else:
                    user_input = self.console.input("[bold green]Admin@VIOLET:~$ [/]")
                
                if not user_input.strip():
                    continue

                if user_input.lower() in ["/v", "voice"]:
                    self.console.print("\n")
                    self.console.print(Panel(
                        "[blink bold red]● MICROPHONE CAPTURE ONLINE - SPEAK NOW...[/]", 
                        border_style="red", 
                        expand=True,
                        title="[bold yellow]Voice Channel Link[/]"
                    ))
                    # Give beep alert if on Windows
                    if os.name == 'nt':
                        try:
                            import winsound
                            winsound.Beep(1000, 250)
                        except:
                            pass
                    
                    user_input = self.ears.record_and_transcribe(seconds=5)
                    
                    if not user_input or not user_input.strip():
                        self.console.print("[yellow]No speech detected or audio channel closed.[/]")
                        continue
                    
                    self.console.print(f"[bold green]Voice Transcribed:[/] {user_input}\n")

                if user_input.lower() in ["exit", "quit", "shutdown", "bye"]:
                    self.console.print("[bold red]Shutting down system interface...[/]")
                    self.mouth.speak("System shutting down. Goodbye, Sir.")
                    time.sleep(1.5)
                    break
                    
                if user_input.lower() == "/clear":
                    self.brain.memory.clear_memory()
                    self.console.print("[bold green]Sqlite context memory cleared successfully.[/]")
                    continue

                # Run chat process under Live display spinner
                final_response = ""
                with Live(Spinner("bouncingBar", text="[bold cyan]VIOLET PROCESSING...", style="cyan"), transient=True) as live:
                    for chunk in self.brain.chat(user_input):
                        if chunk.startswith("SYSTEM:"):
                            live.update(Spinner("bouncingBar", text=f"[bold yellow]{chunk}", style="yellow"))
                        else:
                            final_response = chunk
                
                self.console.print(Panel(
                    final_response, 
                    title="[bold magenta]VIOLET RESPONSE[/]", 
                    border_style="magenta", 
                    padding=(1, 2)
                ))
                
                # Speak output
                if not self.is_muted:
                    self.mouth.speak(final_response)

            except KeyboardInterrupt:
                self.console.print("\n[bold red]Interrupted. Write 'exit' to shut down safely.[/]")
            except Exception as e:
                self.console.print(Panel(f"[bold red]CRITICAL SYSTEM ERROR:[/]\n{str(e)}", border_style="red"))

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.mouth.enabled = not self.is_muted
        self.console.print(f"\n[dim]VIOLET speaker output: {'MUTED' if self.is_muted else 'ACTIVE'}[/]\n", end="")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    cli = VioletCLI()
    cli.run()
