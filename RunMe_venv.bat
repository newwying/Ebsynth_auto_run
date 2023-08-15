@echo off
cd %~dp0

REM Activate the virtual environment
call .\ebsynth_auto_run_venv\Scripts\activate

python gui_app.py
pause
