import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import Ebsynth_auto_run_gui  # 请替换为您原始脚本的名称
import threading
import configparser
import sys
import os
import time

all_widgets = []
START = "start"
PAUSE = "pause"
RESUME = "resume"
current_state = START


def display_initial_info():
    """显示初始化信息到输出文本框中"""
    custom_print_to_gui("=" * 50)
    custom_print_to_gui("      Welcome to Ebsynth Auto Run Tool")
    custom_print_to_gui("=" * 50)
    custom_print_to_gui("Developed by: newwying")
    custom_print_to_gui("Open Source Repository And Usage Methods:")
    custom_print_to_gui("https://github.com/newwying/Ebsynth_auto_run")
    custom_print_to_gui("=" * 50)
    custom_print_to_gui("\n")  # 一个空行作为分隔


def load_config():
    config_path = os.path.join(sys._MEIPASS, 'ebsynth_auto_run_config.ini') if getattr(
        sys, 'frozen', False) else 'ebsynth_auto_run_config.ini'

    config = configparser.ConfigParser()
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config.read_file(config_file)

    # ... (rest of the function)

    # 设置变量的值
    mask_control_var.set(config.getboolean('DEFAULT', 'Mask_control'))
    max_workers_var.set(config.getint('DEFAULT', 'Max_workers'))
    wait_exit_var.set(config.getboolean('DEFAULT', 'WAIT_EXIT_REMOTE_DESKTOP'))


def flatten_to_str_list(item):
    """Recursively flatten an item to a list of strings."""
    if isinstance(item, (list, tuple)):
        return [subitem for sublist in item for subitem in flatten_to_str_list(sublist)]
    else:
        return [str(item)]


def custom_print_to_gui(*args, **kwargs):
    flat_str_list = [
        str_item for item in args for str_item in flatten_to_str_list(item)]
    output_str = ' '.join(flat_str_list) + '\n'
    output_text.insert(tk.END, output_str)
    output_text.see(tk.END)  # Auto-scroll to the bottom of the text widget


Ebsynth_auto_run_gui.custom_print = custom_print_to_gui


def toggle_mask_control():
    current_value = mask_control_var.get()
    new_value = not current_value
    mask_control_var.set(new_value)
    if new_value:
        mask_control_btn.config(text='Mask Control: ON', bg='lightgreen')
    else:
        mask_control_btn.config(text='Mask Control: OFF', bg='lightcoral')


def toggle_wait_exit():
    current_value = wait_exit_var.get()
    new_value = not current_value
    wait_exit_var.set(new_value)
    if new_value:
        wait_exit_btn.config(text='Wait Exit: ON', bg='lightgreen')
    else:
        wait_exit_btn.config(text='Wait Exit: OFF', bg='lightcoral')


def toggle_start():
    global current_state
    if current_state == START:
        # Start the process or operation
        # Change the button label to "Pause"
        start_button.config(text="Pause", bg='lightcoral')
        # Update the current state
        current_state = PAUSE
        root.attributes('-toolwindow', True)
        root.attributes('-topmost', True)
        start_program()
    elif Ebsynth_auto_run_gui.terminate_program:
        start_button.config(text="Start", bg='lightgreen')
        # Update the current state
        current_state = START
        root.attributes('-toolwindow', False)
        root.attributes('-topmost', False)
    elif current_state == PAUSE:
        # Pause the process or operation
        Ebsynth_auto_run_gui.pause_event.clear()
        # Change the button label to "Resume"
        start_button.config(text="Resume", bg='lightgreen')
        # Update the current state
        current_state = RESUME
        root.attributes('-toolwindow', False)
        root.attributes('-topmost', False)
    elif current_state == RESUME:
        # Resume the process or operation
        Ebsynth_auto_run_gui.pause_event.set()
        # Change the button label back to "Pause"
        start_button.config(text="Pause", bg='lightcoral')
        # Update the current state back to PAUSE
        current_state = PAUSE
        root.attributes('-toolwindow', True)
        root.attributes('-topmost', True)


def select_directory():
    directory = filedialog.askdirectory(mustexist=True)
    # 如果用户选择了目录，则更新，否则保持原始值
    if directory:
        directory_var.set(directory)
        Ebsynth_auto_run_gui.project_directory = directory


def select_files():
    paths = filedialog.askopenfilenames(title="Select Directory or Files",
                                        filetypes=[("EBS Files", "*.ebs")])

    if paths:
        # 获取所有文件名，使用os.path.basename
        ebs_files = [os.path.basename(path) for path in paths]

        # 获取所有文件的公共目录，使用os.path.dirname
        common_directory = os.path.dirname(paths[0])
        directory_var.set(';'.join(ebs_files))
        Ebsynth_auto_run_gui.ebs_files = ebs_files
        Ebsynth_auto_run_gui.project_directory = common_directory


def disable_all_widgets():
    for widget in all_widgets:
        widget.config(state=tk.DISABLED)


def enable_all_widgets():
    for widget in all_widgets:
        widget.config(state=tk.NORMAL)
    terminate_button.config(state=tk.DISABLED)


def monitor_thread(thread):
    thread.join()  # Wait for the main program thread to finish
    if Ebsynth_auto_run_gui.failed_filename:
        failed_filename = sorted(
            list(set(Ebsynth_auto_run_gui.failed_filename)))
        # Show a message box to the user
        error_message = "The following files had errors:\n{}\nDo you want to retry these files?".format(
            '\n'.join(failed_filename))
        response = messagebox.askyesno("Error", error_message)

        if response:
            # Call the function to retry processing the failed files
            enable_all_widgets()
            retry_failed_files()
            return
    toggle_start()
    enable_all_widgets()  # Enable all widgets after the thread completes
    # Ebsynth_auto_run_gui.ebs_files = []
    Ebsynth_auto_run_gui.failed_filename = []


def retry_failed_files():
    global current_state
    # Logic to retry processing the failed files
    # Update the current state
    current_state = START
    toggle_start()


def start_program():
    Ebsynth_auto_run_gui.terminate_program = False  # Reset the termination flag
    Ebsynth_auto_run_gui.Mask_control = mask_control_var.get()
    # 限制 Max Workers 的值在 1-15 之间
    workers = max_workers_var.get()
    if workers < 1:
        workers = 1
    elif workers > 15:
        workers = 15
    Ebsynth_auto_run_gui.Max_workers = workers
    Ebsynth_auto_run_gui.WAIT_EXIT_REMOTE_DESKTOP = wait_exit_var.get()
    thread = threading.Thread(target=Ebsynth_auto_run_gui.main)
    thread.start()
    # 禁用所有的按钮和控件
    disable_all_widgets()
    # 单独启用 "Terminate" 按钮
    # 假设您的Terminate按钮的变量名是terminate_button
    terminate_button.config(state=tk.NORMAL)
    start_button.config(state=tk.NORMAL)
    # Create another thread to monitor the main program thread
    monitor = threading.Thread(target=monitor_thread, args=(thread,))
    monitor.start()


def terminate_program():
    Ebsynth_auto_run_gui.terminate_program = True
    # toggle_start()
    # 启用所有的按钮和控件
    enable_all_widgets()
    Ebsynth_auto_run_gui.pause_event.set()


root = tk.Tk()

root.title("Ebsynth Auto Run V1.1")
# 隐藏最小化按钮
root.attributes('-toolwindow', False)
root.attributes('-topmost', False)

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

mask_control_var = tk.BooleanVar(value=True)
max_workers_var = tk.IntVar(value=3)
wait_exit_var = tk.BooleanVar(value=False)
directory_var = tk.StringVar(value=Ebsynth_auto_run_gui.project_directory)

# Mask Control按钮
mask_control_btn = tk.Button(frame, text='Mask Control: ON' if mask_control_var.get() else 'Mask Control: OFF',
                             command=toggle_mask_control, bg='lightgreen' if mask_control_var.get() else 'lightcoral')
mask_control_btn.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
all_widgets.append(mask_control_btn)
# Wait Exit Remote Desktop按钮
wait_exit_btn = tk.Button(frame, text='Wait Exit: ON' if wait_exit_var.get() else 'Wait Exit: OFF',
                          command=toggle_wait_exit, bg='lightgreen' if wait_exit_var.get() else 'lightcoral')
wait_exit_btn.grid(row=0, column=1, columnspan=3, sticky="w", pady=(0, 10))
all_widgets.append(wait_exit_btn)
tk.Label(frame, text="Max Workers").grid(
    row=1, column=0, sticky="w", pady=(0, 10))
spinbox_widget = tk.Spinbox(frame, from_=1, to=15,
                            textvariable=max_workers_var)
spinbox_widget.grid(row=1, column=1, sticky="w", pady=(0, 10))
all_widgets.append(spinbox_widget)

tk.Label(frame, text="Project Directory").grid(
    row=2, column=0, sticky="w", pady=(0, 10))
entry_widget = tk.Entry(frame, textvariable=directory_var)
entry_widget.grid(row=2, column=1, sticky="ew", pady=(0, 10))
all_widgets.append(entry_widget)

select_directory_btn = tk.Button(
    frame, text="Select Directory", command=select_directory)
select_directory_btn.grid(row=2, column=2, pady=(0, 10))
all_widgets.append(select_directory_btn)

select_files_btn = tk.Button(
    frame, text="Select Files", command=select_files)
select_files_btn.grid(row=2, column=3, sticky="w", pady=(0, 10))
all_widgets.append(select_files_btn)

scrollbar = ttk.Scrollbar(frame)
scrollbar.grid(row=3, column=3, sticky="ns")

output_text = tk.Text(frame, height=10, yscrollcommand=scrollbar.set)
output_text.grid(row=3, column=0, columnspan=3, pady=(10, 10))
scrollbar.config(command=output_text.yview)

start_button = tk.Button(
    frame, text="Start", command=toggle_start, bg='lightgreen')
start_button.grid(row=4, column=0, pady=(10, 0))
all_widgets.append(start_button)
terminate_button = tk.Button(
    frame, text="Terminate", command=terminate_program, bg='lightcoral')
terminate_button.grid(row=4, column=2, pady=(10, 0))
all_widgets.append(terminate_button)
terminate_button.config(state=tk.DISABLED)

root.geometry("-400+200")

load_config()

display_initial_info()

root.mainloop()
