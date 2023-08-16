import sys
import shutil
import time
import os
import pyautogui
import winreg
import pygetwindow as gw
import win32gui
import win32print
import win32con
import win32process
import psutil
from PIL import Image
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
import configparser

project_directory = os.getcwd()
original_directory = project_directory


def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发模式和PyInstaller模式 """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def simplify_missing_files(missing_files):
    simplified = []
    i = 0
    while i < len(missing_files):
        start = missing_files[i]
        while (i + 1 < len(missing_files) and
               int(missing_files[i+1].split('.')[0]) -
               int(missing_files[i].split('.')[0]) == 1):
            i += 1
        end = missing_files[i]
        if start == end:
            simplified.append(start)
        else:
            simplified.append(f"{start}-{end}")
        i += 1
    return simplified


def check_missing_files(base_directory, key_frame_folder="video_frame"):
    # 获取 key_frame 文件夹内的所有文件名
    key_frame_path = os.path.join(base_directory, key_frame_folder)
    key_frame_files = set(os.listdir(key_frame_path))

    # 获取所有的生成文件夹
    generated_folders = [d for d in os.listdir(base_directory)
                         if os.path.isdir(os.path.join(base_directory, d))
                         and d.startswith("out-")]

    # 遍历每个生成文件夹，检查其中的文件
    for folder in generated_folders:
        folder_path = os.path.join(base_directory, folder)
        for filename in os.listdir(folder_path):
            key_frame_files.discard(filename)

    # 返回未在生成文件夹中找到的文件
    missing_files = sorted(list(key_frame_files))
    return simplify_missing_files(missing_files)


def get_dpi_scale():
    try:
        hdc = win32gui.GetDC(0)
        dpi = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSX)
        win32gui.ReleaseDC(0, hdc)

        # 根据DPI值计算缩放比例
        scale_percent = int(dpi / 96 * 100)
        return scale_percent
    except Exception as e:
        custom_print(f"Error getting DPI scale from registry: {e}")
        return None


def create_and_copy_to_resized_folder(original_folder, target_folder_name="resize_images"):
    target_folder_path = os.path.join(original_folder, target_folder_name)
    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path)

    for filename in os.listdir(original_folder):
        if filename != target_folder_name:  # 避免复制resize_images文件夹本身
            original_path = os.path.join(original_folder, filename)
            target_path = os.path.join(target_folder_path, filename)
            shutil.copy(original_path, target_path)

    return target_folder_path


def delete_resized_folder(folder_path):
    shutil.rmtree(folder_path)


def resize_images_in_folder(folder_path, scale_factor):
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                with Image.open(file_path) as img:
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                    img_resized = img.resize(
                        (new_width, new_height), Image.BILINEAR)
                    img_resized.save(file_path)
    except Exception as e:
        custom_print(f"Error resizing images in folder: {e}")


def custom_print(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def get_default_program(extension):
    try:
        # 获取扩展名关联的默认程序名
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
            prog_id = winreg.QueryValue(key, None)

        # 使用程序名查询其命令行
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                            f"{prog_id}\\shell\\open\\command") as key:
            command = winreg.QueryValue(key, None)

        # 返回的命令行通常包含"%1"，这是文件路径的占位符
        program_path = command.split('"')[1]
        return program_path
    except Exception as e:
        custom_print(f"Error getting default program for {extension}: {e}")
        return None


def monitor_process(pid, filename):
    try:
        custom_print(f"开始监控 {filename}")
        ps_process = psutil.Process(pid)
        while True:
            if terminate_program:
                ps_process.terminate()
                break
            time.sleep(0.5)
            cpu_percent = ps_process.cpu_percent(interval=1)
            if cpu_percent < 0.5:
                ps_process.terminate()
                custom_print(f"{filename}运行完毕")
                break
    except psutil.NoSuchProcess:
        custom_print(f"{filename}进程不存在")
        failed_files.append(f"{filename}进程不存在")
    except Exception as e:
        custom_print(f"Error monitoring process for {filename}: {e}")


def move_and_resize_window_by_pid(pid, x, y, timeout=5):
    """
    根据给定的进程ID，将窗口移动并调整到指定位置和大小。

    参数:
    - pid: 要查找的进程ID
    - x, y: 窗口左上角的目标位置
    - width, height: 窗口的目标尺寸

    返回:
    - 如果成功，返回窗口的矩形区域坐标，否则返回None
    """
    get_window_time = time.time()

    while time.time() - get_window_time < timeout:
        window = get_window_by_pid(pid)
        if window:
            try:
                win32gui.SetForegroundWindow(window._hWnd)
                window.moveTo(0, 0)
                return window._rect
            except Exception as e:
                custom_print(f"Error moving and resizing window for pid {pid}: {e}")
                return None
        time.sleep(0.5)  # 等待一小段时间再次尝试


def minimize_window_by_pid(pid):
    """
    根据给定的进程ID，最小化窗口。

    参数:
    - pid: 要查找的进程ID
    """
    try:
        window = get_window_by_pid(pid)
        if window:
            win32gui.ShowWindow(window._hWnd, win32con.SW_MINIMIZE)
    except Exception as e:
        custom_print(f"Error minimizing window for pid {pid}: {e}")


def get_window_by_pid(pid):
    for window in gw.getAllWindows():
        hwnd = window._hWnd
        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
        if process_id == pid:
            return window
    return None


def start_program(filename):
    filepath = os.path.join(project_directory, filename)

    # 检查文件是否存在
    if not os.path.exists(filepath):
        custom_print(f"文件 {filepath} 不存在！")
        failed_files.append(f"文件 {filepath} 不存在！")
        return

    file_path = os.path.join(project_directory, filename)

    try:
        process = subprocess.Popen([associated_program, file_path])
        time.sleep(0.2)
        rect = move_and_resize_window_by_pid(process.pid, int(
            200), int(200))
        if rect:
            custom_print(f"Moved and resized window to: {rect}")
        else:
            custom_print("No window found for the given PID.")
    except Exception as e:
        custom_print(f"启动 {file_path} 时出现异常: {e}")
        failed_files.append(f"启动 {file_path} 时出现异常: {e}")
        return

    if process.returncode:
        custom_print(f"启动 {filepath} 时出现问题，返回码: {process.returncode}")
        failed_files.append(f"启动 {filepath} 时出现问题，返回码: {process.returncode}")
        return

    pid = process.pid
    run_ebsynth(filename, pid, rect)


def run_ebsynth(filename, pid, rect):
    # 记录鼠标的当前位置
    original_mouse_position = pyautogui.position()
    try:
        # 是否需要遮罩的判断
        if not Mask_control:
            result_mask = pyautogui.locateCenterOnScreen(os.path.join(
                resized_folder, "zhezhao.png"),
                confidence=0.8,
                region=(rect.left, rect.top, rect.width, rect.height))
            if result_mask:
                pyautogui.click(result_mask)
                custom_print(f"{filename}蒙版关闭完成。")
            else:
                custom_print(f"{filename}蒙版关闭失败！没有找到匹配的图像。")
                failed_files.append(f"{filename}蒙版关闭失败！没有找到匹配的图像。")

        time.sleep(0.2)

        # 找RUNALL按钮并点击

        result_run = pyautogui.locateCenterOnScreen(os.path.join(
            resized_folder, "run.png"),
            confidence=0.8, region=(rect.left, rect.top, rect.width, rect.height))
        if result_run:
            # runall_x, runall_y = result_run
            pyautogui.click(result_run)
            custom_print(f"{filename}Run All点击完成。")
            time.sleep(3.0)
            minimize_window_by_pid(pid)

        else:
            custom_print(f"{filename}Run All点击失败！没有找到匹配的图像。")
            failed_files.append(f"{filename}Run All点击失败！没有找到匹配的图像。")
    except Exception as e:
        custom_print(f"Error while processing {filename}: {str(e)}")
        failed_files.append(f"Error while processing {filename}: {str(e)}")
    finally:
        # 将鼠标移回原来的位置
        pyautogui.moveTo(
            original_mouse_position[0], original_mouse_position[1])
    monitor_process(pid, filename)
    time.sleep(0.2)
    semaphore.release()  # 任务完成后释放 permit


def main():
    start_time = time.time()
    global Mask_control, Max_workers, WAIT_EXIT_REMOTE_DESKTOP
    global project_directory, associated_program, resized_folder, original_directory
    global failed_files, semaphore, terminate_program
    # config = configparser.ConfigParser()
    # with open('ebsynth_auto_run_config.ini', 'r', encoding='utf-8') as config_file:
    #     config.read_file(config_file)

    # Mask_control = config.getboolean('DEFAULT', 'Mask_control')
    # Max_workers = config.getint('DEFAULT', 'Max_workers')
    # WAIT_EXIT_REMOTE_DESKTOP = config.getboolean(
    #     'DEFAULT', 'WAIT_EXIT_REMOTE_DESKTOP')

    failed_files = []
    semaphore = threading.Semaphore(Max_workers)
    terminate_program = False
    if WAIT_EXIT_REMOTE_DESKTOP:
        custom_print("开始等待，请在30秒内退出远程桌面！")
        time.sleep(30)
    extension = ".ebs"
    associated_program = get_default_program(extension)
    custom_print(f" {extension} 的可执行程序位置: \n{associated_program}")
    scaling = get_dpi_scale()
    if scaling:
        custom_print(f"系统缩放比例: {scaling}%")
    else:
        custom_print("Unable to determine system scaling from the registry.")
    overall_scale_factor = scaling / 100
    try:
        # 在调整图像大小之前调用此函数
        # resized_folder = create_and_copy_to_resized_folder(
        #     os.path.join(original_directory, "Ebsynth_auto_run_png"))
        resized_folder = create_and_copy_to_resized_folder(
            resource_path("Ebsynth_auto_run_png"))
        resize_images_in_folder(resized_folder, overall_scale_factor)
        custom_print("按钮图片重载完成!")
    except Exception as e:
        custom_print(f"重载按钮图片失败: {e}")
    custom_print("开始Ebsynth自动化。")

    subprocess.run(r'dir *.ebs /b > lists.txt',
                   shell=True, cwd=project_directory)

    ebs_list_file = os.path.join(project_directory, "lists.txt")

    # 文件全名——参数设置
    with open(ebs_list_file, 'r', encoding='utf-8') as file:
        ebs_files = [line.strip() for line in file.readlines()]

    # 使用线程池来监控这个进程
    # 设置最大工作线程数为3，可以根据需要调整
    with ThreadPoolExecutor(max_workers=Max_workers) as executor:
        # 开始工作次数的循环
        for wenjianming in ebs_files[:]:
            semaphore.acquire()  # 尝试获取一个 permit
            if terminate_program:
                break
            # executor.submit(custom_print, wenjianming)
            executor.submit(start_program, wenjianming)
            time.sleep(5)
    if terminate_program:
        custom_print("*****程序已终止")
    else:
        custom_print("全部文件运行完毕！！！")
    if failed_files:
        custom_print("*****运行以下文件出现了错误：", failed_files)
    try:
        # 检查生成的文件完整性
        missing_files = check_missing_files(project_directory)
        if not missing_files:
            custom_print("Ebsynth生成图片完整性检查通过！")
        else:
            custom_print("*****Ebsynth没有生成图片:", missing_files)
    except Exception as e:
        custom_print(f"Error check_missing_files: {e}")
    # 在程序的最后，删除resize_images文件夹
    delete_resized_folder(resized_folder)
    end_time = round(time.time() - start_time, 1)
    custom_print(f"总共用时：{end_time} s")
