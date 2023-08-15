# Ebsynth Automation Tool

## Introduction:
This tool aims to automate the Ebsynth operation process.

## Installation:
1. Clone the GitHub repository or download the ZIP file.
2. Use the appropriate Python environment (developed on Python3.9 locally).
3. Navigate to the directory using `cd` followed by the directory path in the command line.
4. Install the required dependencies (you can switch to Tsinghua source if there's an internet issue):
    ```
    pip install -r requirements.txt
    ```

## Configuration (can also be modified in the GUI):
Use `ebsynth_auto_run_config.ini` for configuration. You can edit the following parameters:
- **Mask_control**: Whether you need a mask (Mask Control button). If not needed, set to False. Default is True.
- **Max_workers**: Number of ebsynth files to run simultaneously, depending on your computer's capacity. Default is 3.
- **WAIT_EXIT_REMOTE_DESKTOP**: Exit remote desktop within 30 seconds. Remote desktop might impact mouse clicks (you can try it out first). There's no delay by default; change to True if needed. Default is False.

## Usage:
1. Double-click `RunMe.bat`.
2. Select the directory of the ebs files you wish to automate.
3. Click `Start` to begin automation.
4. After starting the program, do not move the mouse to the corners of the screen, as it may cause program errors.
5. Once the program completes, it will automatically check the integrity of ebs output files against the image sequence in the `video_frame` folder. If there are no missing parts, it will return "Ebsynth generated image integrity check passed!".
![GUI Schematic](./images/gui.png)

## Termination:
At any time, you can click `Terminate` to stop the program.

## Troubleshooting:
1. Ensure that all image files and Ebsynth files are in the correct directories.
2. If you encounter issues, check the configuration in `ebsynth_auto_run_config.ini` or refer to the error messages in the output section.

## Note:
- This tool automates the Ebsynth process. Ensure you have the necessary permissions and all the dependencies.
- It's a good idea to do a manual test before using it to make sure everything is working properly.
