@echo off
setlocal
title VIOLET SYSTEM - CORE
color 05

:: Set directory to script location
cd /d "%~dp0"

echo -----------------------------------------------------------------------------
echo                            VIOLET BOOT SEQUENCE
echo -----------------------------------------------------------------------------

:: 1. Check for Admin Privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Administrative privileges confirmed.
) else (
    echo [!!] WARNING: Not running as Administrator. Some tools may fail.
    echo      Right-click this file and select 'Run as Administrator' for full power.
    timeout /t 3
)

:: 2. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b
)
echo [OK] Python detected.

:: 3. Check Dependencies (Silent install)
echo [SYSTEM] Verifying core modules...
pip install -r requirements.txt --quiet
echo [OK] Core modules ready.

:: 4. Check Ollama
echo [SYSTEM] Pinging Ollama Engine...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is not running. Please start Ollama to proceed.
    pause
    exit /b
)
echo [OK] Ollama link established.

echo -----------------------------------------------------------------------------
echo                          LAUNCHING VIOLET INTERFACE
echo -----------------------------------------------------------------------------
cls
python main.py
if %errorlevel% neq 0 (
    echo [SYSTEM] VIOLET has encountered a terminal error.
    pause
)
