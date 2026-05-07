import time
import os
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner
from rich.layout import Layout
from rich.table import Table
from brain import VioletBrain
from voice import VioletVoice
from tools import VioletTools

class VioletUI:
    def __init__(self):
        self.brain = VioletBrain()
        self.voice = VioletVoice()
        self.console = Console()
        self.tools = VioletTools()

    def welcome_screen(self):
        self.console.clear()
        self.console.print(Panel(
            Text("VIOLET SYSTEM ONLINE", style="bold magenta", justify="center"),
            subtitle="Advanced Agentic AI System Administrator v2.0",
            border_style="cyan",
            expand=True
        ))
        
        # Connection check
        connected = False
        msg = ""
        with self.console.status("[bold cyan]Establishing link to Ollama...", spinner="dots"):
            connected, msg = self.brain.check_connection()
            time.sleep(1) # For dramatic effect
            
        if connected:
            # Model Selection (outside the status spinner so input works)
            models = self.brain.get_available_models()
            if not models:
                self.console.print("[bold red]ERROR:[/] No models found in Ollama. Please run 'ollama pull llama3' first.")
                exit(1)
            elif len(models) == 1:
                selected_model = models[0]
                self.brain.set_model(selected_model)
                self.console.print(f"[bold green]OK:[/] Connection to {selected_model} established.")
            else:
                self.console.print(f"[bold green]OK:[/] {msg}")
                self.console.print("\n[bold white]Available Intelligence Engines:[/]")
                for idx, m in enumerate(models, 1):
                    self.console.print(f"  [bold cyan]{idx}.[/] {m}")
                
                while True:
                    try:
                        choice = self.console.input("\n[bold yellow]Select Engine (1-{0}):[/] ".format(len(models)))
                        idx = int(choice) - 1
                        if 0 <= idx < len(models):
                            selected_model = models[idx]
                            self.brain.set_model(selected_model)
                            self.console.print(f"[bold green]OK:[/] Connection to {selected_model} established.\n")
                            break
                        else:
                            self.console.print("[red]Invalid selection. Try again.[/]")
                    except ValueError:
                        self.console.print("[red]Please enter a number.[/]")
        else:
            self.console.print(f"[bold red]ERROR:[/] {msg}")
            self.console.print("[yellow]Please ensure Ollama is running and restart VIOLET.[/]")
            exit(1)

    def get_status_panel(self):
        metrics = self.tools.get_system_metrics().split("\n")
        cpu = metrics[0]
        ram = metrics[1]
        cwd = os.getcwd()
        
        table = Table(show_header=False, border_style="dim")
        table.add_row("CPU", f"[magenta]{cpu.split(': ')[1]}[/]")
        table.add_row("RAM", f"[magenta]{ram.split(': ')[1]}[/]")
        table.add_row("CWD", f"[dim]{cwd}[/]")
        
        return Panel(table, title="[bold white]System Status[/]", border_style="blue")

    def run(self):
        self.welcome_screen()
        
        # Setup global hotkey for muting voice
        try:
            import keyboard
            keyboard.add_hotkey('ctrl+m', lambda: self.console.print(f"\n[dim]Voice Muted: {self.voice.toggle_mute()}[/]\n", end=""))
        except ImportError:
            self.console.print("[yellow]Warning: 'keyboard' module not installed. Hotkeys disabled.[/]")
            
        self.console.print("[dim]Hint: Type '/v' to use voice commands. Press 'Ctrl+M' to toggle mute.[/]")
        
        while True:
            try:
                # Show status panel and wait for input
                self.console.print(self.get_status_panel())
                user_input = self.console.input("[bold green]Admin@VIOLET:~$ [/]")
                
                if not user_input.strip():
                    continue

                if user_input.lower() == '/v' or user_input.lower() == 'voice':
                    with self.console.status("[bold cyan]Listening for Voice Command...", spinner="dots"):
                        user_input = self.voice.listen()
                    
                    if not user_input:
                        self.console.print("[yellow]No speech detected. Try again.[/]")
                        continue
                    
                    self.console.print(f"[bold yellow]Transcribed:[/] {user_input}")

                if user_input.lower() in ["exit", "quit", "shutdown"]:
                    self.console.print("[bold red]Shutting down VIOLET...[/]")
                    self.voice.speak("System shutting down. Goodbye.")
                    break
                
                with Live(Spinner("bouncingBar", text="[bold cyan]VIOLET PROCESSING...", style="cyan"), transient=True):
                    response = self.brain.chat(user_input)
                
                self.console.print(Panel(response, title="[bold magenta]VIOLET[/]", border_style="magenta", padding=(1, 2)))
                self.voice.speak(response)
                
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Interrupted. Type 'exit' to shutdown.[/]")
            except Exception as e:
                self.console.print(Panel(f"[bold red]SYSTEM ERROR:[/]\n{str(e)}", border_style="red"))

if __name__ == "__main__":
    ui = VioletUI()
    ui.run()
