import tkinter as tk
from tkinter import filedialog, ttk
import Ebsynth_auto_run_gui  # 请替换为您原始脚本的名称
import threading
import configparser
import sys

all_widgets = []

def display_initial_info():
    """显示初始化信息到输出文本框中"""
    custom_print_to_gui("=" * 50)
    custom_print_to_gui("      Welcome to Ebsynth Auto Run Tool")
    custom_print_to_gui("=" * 50)
    custom_print_to_gui("Developed by: newwying")
    custom_print_to_gui("Open Source Repository:")
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


def select_directory():
    directory = filedialog.askdirectory()
    # 如果用户选择了目录，则更新，否则保持原始值
    if directory:
        directory_var.set(directory)
        Ebsynth_auto_run_gui.project_directory = directory


def disable_all_widgets():
    for widget in all_widgets:
        widget.config(state=tk.DISABLED)


def enable_all_widgets():
    for widget in all_widgets:
        widget.config(state=tk.NORMAL)
    terminate_button.config(state=tk.DISABLED)


def monitor_thread(thread):
    thread.join()  # Wait for the main program thread to finish
    enable_all_widgets()  # Enable all widgets after the thread completes


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
    # Create another thread to monitor the main program thread
    monitor = threading.Thread(target=monitor_thread, args=(thread,))
    monitor.start()


def terminate_program():
    Ebsynth_auto_run_gui.terminate_program = True
    # 启用所有的按钮和控件
    enable_all_widgets()


root = tk.Tk()

root.title("Ebsynth Auto Run")
# 隐藏最小化按钮
root.attributes('-toolwindow', True)

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

scrollbar = ttk.Scrollbar(frame)
scrollbar.grid(row=3, column=3, sticky="ns")

output_text = tk.Text(frame, height=10, yscrollcommand=scrollbar.set)
output_text.grid(row=3, column=0, columnspan=3, pady=(10, 10))
scrollbar.config(command=output_text.yview)

start_button = tk.Button(
    frame, text="Start", command=start_program, bg='lightgreen')
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
root.attributes('-topmost', True)
root.mainloop()
