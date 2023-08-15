@echo off
REM 检查 ebsynth 虚拟环境是否已存在
if not exist "ebsynth_auto_run_venv\Scripts\activate" (
    echo Creating virtual environment: ebsynth_auto_run_venv
    python -m venv ebsynth_auto_run_venv
) else (
    echo Virtual environment ebsynth already exists.
)

REM 激活虚拟环境
call ebsynth_auto_run_venv\Scripts\activate.bat

pip install -r requirements.txt

REM 打开命令行，保持虚拟环境激活状态
cmd /k
