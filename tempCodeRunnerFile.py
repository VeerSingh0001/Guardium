import os
import pyclamd
import eel
import platform
import psutil
import pyautogui
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

eel.init("web")


class Anti:
    def __init__(self):
        self.lock = Lock()
        self.partitions = []

    # Connect to the ClamAV daemon
    def connect_to_guardium(self):
        try:
            cd = pyclamd.ClamdNetworkSocket()  # Use network socket connection
            if cd.ping():
                print("Connected to Guardium daemon")
                return cd
            else:
                print("Failed to connect to Guardium daemon")
                return None
        except pyclamd.ConnectionError:
            print("Could not connect to Guardium daemon.")
            return None

    #  Count the total number of files to be scanned
    def count_files(self, typ):
        file_count = 0
        if typ == "quick":
            self.partitions = [
                "C:\\Windows\\System32",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Temp"),
                os.path.expandvars("%USERPROFILE%\\AppData\\Roaming"),
            ]
        elif typ == "full":
            all_partitions = psutil.disk_partitions()
            for part in all_partitions:
                # print(part.device)
                self.partitions.append(part.device)
            print(self.partitions)
        else:
            pass

        for partition in self.partitions:
            directory = partition.replace("\\", "/")

            for root, dirs, files in os.walk(directory):
                file_count += len(files)
            print(f"Total number of files: {file_count}")
            return file_count

    # Scan a directory
    def scan_directory(self, cd, directory_path):
        with ThreadPoolExecutor(max_workers=1000) as executor:  # Adjust max_workers based on your CPU
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    executor.submit(self.scan_a_file, cd, file_path)

    # Scan a single file
    def scan_a_file(self, cd, file_path):
        try:

            with self.lock:
                result = cd.scan_file(rf"{file_path}")
            if result is None:
                print(f"{file_path} is clean")
            else:
                print(f"Virus found in {file_path}: {result}")
        except Exception as e:
            # with self.lock:
            #     print(f"Error scanning file {file_path}: {e}")
            #     print(f"File causing issue: {file_path}")
            print(f"Error scanning file {file_path}: {e}")


@eel.expose
def start_scan():
    anti = Anti()
    clamd_instance = anti.connect_to_guardium()
    anti.count_files("quick")
    if clamd_instance:
        for par in anti.partitions:
            anti.scan_directory(clamd_instance, par)


screen_reso = pyautogui.size()

try:
    eel.start(
        "index.html",
        port=0,
        mode="chrome",
        size=(screen_reso.width, screen_reso.height),
    )
except EnvironmentError:
    # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
    if sys.platform in ["win32", "win64"] and int(platform.release()) >= 10:
        eel.start(
            "index.html",
            port=0,
            mode="edge",
            size=(screen_reso.width, screen_reso.height),
        )
    else:
        raise EnvironmentError("Error: System is not Windows 10 or above")
except (SystemExit, KeyboardInterrupt):
    sys.exit(0)
