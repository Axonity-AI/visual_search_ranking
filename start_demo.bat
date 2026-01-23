@echo off
REM Visual Search Demo - One-Click Startup (Windows)

setlocal EnableDelayedExpansion

set BACKEND_PORT=8000
set STATIC_PORT=8001
set DEMO_URL=http://localhost:%STATIC_PORT%/enterprise_demo/frontend_product/index.html

echo.
echo ==========================================
echo   Visual Search Demo - Starting...
echo ==========================================
echo.

REM Check if in correct directory
if not exist "enterprise_demo\" (
    echo ERROR: Run this from Workbench\ directory
    pause
    exit /b 1
)

REM Activate conda environment
echo Activating vis_similarity environment...
call conda activate vis_similarity
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate vis_similarity conda environment
    echo Please create it first: conda create -n vis_similarity python=3.9
    pause
    exit /b 1
)

REM Check ports
netstat -ano | findstr ":%BACKEND_PORT% " | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ERROR: Port %BACKEND_PORT% in use. Run stop_demo.bat first.
    pause
    exit /b 1
)

REM Start backend
echo Starting backend server...
start "Visual Search - Backend" /MIN cmd /c "conda activate vis_similarity && cd enterprise_demo\backend\app && python main.py > ..\..\..\logs\backend.log 2>&1"

REM Wait for backend
echo Waiting for backend (8 seconds)...
timeout /t 8 /nobreak >nul

REM Start static server
echo Starting static server...
start "Visual Search - Static Server" /MIN cmd /c "conda activate vis_similarity && python -m http.server %STATIC_PORT% > logs\static.log 2>&1"

timeout /t 2 /nobreak >nul

REM Open browser
echo Opening browser...
start "" "%DEMO_URL%"

echo.
echo ==========================================
echo   Demo Started!
echo ==========================================
echo.
echo Backend:  http://localhost:%BACKEND_PORT%
echo Demo:     %DEMO_URL%
echo.
echo Close the minimized windows to stop servers
echo Or run: stop_demo.bat
echo.

pause
endlocal
