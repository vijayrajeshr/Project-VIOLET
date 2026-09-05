@echo off
setlocal enabledelayedexpansion
title VIOLET CORE SYSTEM CONTROL
color 0d

:: Set execution directory to current file directory location
cd /d "%~dp0"

echo =============================================================================
echo                         VIOLET CORE BOOT SEQUENCE
echo =============================================================================

:: 1. Admin Privilege check & Auto-Elevation
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Administrative privileges confirmed.
) else (
    echo [SYSTEM] Admin elevation required. Requesting privilege escalation...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

:: 2. Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not detected on system PATH environment.
    echo Please install Python 3.10+ and select "Add to PATH" in installer.
    pause
    exit /b
)
echo [OK] Python runtime environment verified.

:: 3. Run Silent dependency package verification
echo [SYSTEM] Resolving module dependencies from requirements.txt...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Some python modules failed to install cleanly. VIOLET might degrade.
) else (
    echo [OK] Module dependencies confirmed.
)

:: 4. Verify local server connectivity based on backend
set BACKEND=lm-studio
for /f "tokens=2 delims==" %%a in ('findstr /i "LLM_BACKEND" .env') do (
    set BACKEND=%%a
    set BACKEND=!BACKEND: =!
)

if "!BACKEND!"=="lm-studio" (
    echo [SYSTEM] Pinging LM Studio local server...
    curl -s http://localhost:1234/v1/models >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] LM Studio server is not active on http://localhost:1234.
        echo Please launch LM Studio and start the local server to proceed.
        echo.
    ) else (
        echo [OK] LM Studio connection established.
    )
) else if "!BACKEND!"=="ollama" (
    echo [SYSTEM] Pinging Ollama Server link...
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Ollama is not active on http://localhost:11434.
        echo Please start the Ollama desktop application to utilize default intelligence engine.
        echo.
    ) else (
        echo [OK] Ollama connection established.
    )
) else (
    echo [SYSTEM] Local Hugging Face transformers configured. No server checks required.
)

:: 5. Launch Option Selection
echo =============================================================================
echo                         VIOLET SYSTEMS SELECTION
echo =============================================================================
echo  [1] Launch Cyberpunk Web Dashboard (Recommended - http://localhost:8000)
echo  [2] Launch administrative CLI Terminal
echo.
set /p opt="Select System Interface [Default is 1]: "

if "%opt%"=="2" (
    cls
    echo Launching VIOLET CLI Console...
    python main.py --cli
) else (
    cls
    echo Launching VIOLET Web Control Server...
    python main.py --web
)

if %errorlevel% neq 0 (
    echo [SYSTEM ERROR] VIOLET exited with errors.
    pause
)
