import os

import eel
import platform
import psutil
import pyautogui
import sys

eel.init("web")


#  Count the total number of files to be scanned
def count_files_os_walk(type):
    file_count = 0
    partitions = []
    if type == "quick":
        partitions = [
            "C:\\Windows\\System32",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Temp"),
            os.path.expandvars("%USERPROFILE%\\AppData\\Roaming"),
        ]
    elif type == "full":
        all_partitions = psutil.disk_partitions()
        for part in all_partitions:
            partitions.append(part.device)
    else:
        pass #Custom scan files list

    for partition in partitions:
        directory = partition.replace("\\", "/")

        for root, dirs, files in os.walk(directory):
            file_count += len(files)
    print(f"Total number of files: {file_count}")
    return file_count


@eel.expose
def scan_files():
    count_files_os_walk("quick")


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
