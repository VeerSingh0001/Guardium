import ctypes

from elevate import elevate
import os
import pyclamd
import eel
import platform
import psutil
import pyautogui
import sys, subprocess

elevate()

eel.init("web")


# Connect to the ClamAV daemon
def connect_to_clamd():
    try:
        cd = pyclamd.ClamdNetworkSocket()  # Use network socket connection
        if cd.ping():
            print("Connected to ClamAV daemon")
            return cd
        else:
            print("Failed to connect to ClamAV daemon")
            return None
    except pyclamd.ConnectionError:
        print("Could not connect to ClamAV daemon.")
        return None


#  Count the total number of files to be scanned
def count_files_os_walk(typ):
    file_count = 0
    global partitions
    if typ == "quick":
        partitions = [
            "C:\\Windows\\System32",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Temp"),
            os.path.expandvars("%USERPROFILE%\\AppData\\Roaming"),
        ]
    elif typ == "full":
        all_partitions = psutil.disk_partitions()
        for part in all_partitions:
            partitions.append(part.device)
    else:
        pass  # Custom scan files list

    for partition in partitions:
        directory = partition.replace("\\", "/")

        for root, dirs, files in os.walk(directory):
            file_count += len(files)
    print(f"Total number of files: {file_count}")
    return file_count


# Scan a directory
def scan_directory(cd, directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = fr"{os.path.join(root, file)}"
            scan_file(cd, file_path)


# Scan a single file
def scan_file(cd, file_path):
    try:
        result = cd.scan_file(file_path)
        if result is None:
            print(f"{file_path} is clean")
        else:
            print(f"Virus found in {file_path}: {result}")
    except Exception as e:
        print(f"Error scanning file {file_path}: {e}")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


@eel.expose
def scan_files():
    print("Starting Service.....")
    command = "net start clamd"
    if is_admin():
        result = (subprocess.run(command, capture_output=True, text=True))
        print(result)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
    clamd_instance = connect_to_clamd()
    count_files_os_walk("full")
    if clamd_instance:
        for par in partitions:
            scan_directory(clamd_instance, par)


partitions = []

screen_reso = pyautogui.size()

try:
    eel.start("index.html", mode="chrome", size=(screen_reso.width, screen_reso.height))
except EnvironmentError:
    # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
    if sys.platform in ["win32", "win64"] and int(platform.release()) >= 10:
        eel.start(
            "index.html", mode="edge", size=(screen_reso.width, screen_reso.height)
        )
    else:
        raise EnvironmentError("Error: System is not Windows 10 or above")
