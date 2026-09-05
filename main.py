import os
import argparse
import sys
import uvicorn
from dotenv import load_dotenv

# Load workspace environment configurations
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="VIOLET: Next-Generation PC Piloting Assistant")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cli", "-c", 
        action="store_true", 
        help="Launch the Rich-based Terminal Console interface"
    )
    group.add_argument(
        "--web", "-w", 
        action="store_true", 
        help="Launch the FastAPI Web Control Dashboard (Default)"
    )
    
    args = parser.parse_args()

    # Determine default route launcher (default is Web Dashboard)
    run_web = args.web or not args.cli

    if run_web:
        print("[LAUNCHER] Booting VIOLET Web Interface on http://127.0.0.1:8000 ...")
        # uvicorn.run needs the import path as string to load correctly
        uvicorn.run("interfaces.web:app", host="127.0.0.1", port=8000, log_level="info", reload=False)
    else:
        print("[LAUNCHER] Booting VIOLET Terminal Console Interface...")
        from interfaces.cli import VioletCLI
        cli = VioletCLI()
        cli.run()

if __name__ == "__main__":
    main()
