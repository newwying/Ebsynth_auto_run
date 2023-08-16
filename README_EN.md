# Ebsynth Automation Tool

## Introduction:
This tool is designed to automate the Ebsynth workflow.

## Direct Use (No Installation Needed):
Double-click to run `ebsynth_auto_run_app.exe`.

## Installation (If you encounter issues, try installing in a virtual environment):
1. Clone the GitHub repository or download the ZIP file.
2. Use the appropriate Python environment (developed on Python3.9 locally).
3. In the command line, navigate to the directory using `cd` followed by the `directory path`, e.g., `cd C:\Users\Downloads\Ebsynth_auto_run-main`.
4. Install the necessary dependencies (replace with Tsinghua source if there are network issues):
    ```
    pip install -r requirements.txt
    ```

## Installation in a Virtual Environment:
1. Double-click to run `create_venv.bat`.

## Configuration (Can also be modified in the GUI):
Use `ebsynth_auto_run_config.ini` for configuration. You can edit the following parameters:
- **Mask_control**: Determine if you need a mask (overlay button). Set to False if not needed. Default is True.
- **Max_workers**: Number of Ebsynth files to run simultaneously, depending on your computer's capacity. Default is 3.
- **WAIT_EXIT_REMOTE_DESKTOP**: Exit remote desktop within 30 seconds. Remote desktop might affect mouse clicks (you can test it first). Default is no delay; set to True if needed. Default is False.

## Usage:
1. Double-click to run `RunMe.bat` (In a virtual environment, double-click to run `RunMe_venv.bat`).
2. Select the directory of the ebs files you want to automate.
3. Click `Start` to begin automation.
![GUI Schematic](./images/gui.png)

## Termination:
At any time, you can click `Terminate` to stop the program.

## Points to Note:
1. Ensure all image files and Ebsynth files are in the correct directory.
2. If you encounter issues, check if `ebsynth_auto_run_config.ini` is configured correctly or refer to the error messages in the output bar.
3. After starting the program, do not move the mouse to the screen corners, as it may cause errors!
4. After starting the program, keep the GUI at the forefront!
5. After the program finishes running, it will automatically check for missing image sequences in the `video_frame` folder compared to ebs output files. If none are missing, it will return "Ebsynth image integrity check passed!".

## Caution:
- This tool automates the Ebsynth process, ensure you have the necessary permissions and all dependencies.
- Before using, it's a good practice to run a manual test to ensure everything is working properly.

---