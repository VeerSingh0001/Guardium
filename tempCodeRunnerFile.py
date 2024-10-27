import asyncio
import os
import pyclamd
import eel
import platform
import psutil
import pyautogui
import sys
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import ctypes
import pyclamd
from win32security import GetFileSecurity, OWNER_SECURITY_INFORMATION, LookupAccountSid


# Connect to the ClamAV daemon
def connect_to_guardium():
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


# Count the total files number in the directory
def count_files_in_directory(directory):
    file_count = 0
    try:
        for _, _, files in os.walk(directory):
            file_count += len(files)
    except Exception as e:
        print(f"Error counting files in {directory}: {e}")
    return file_count


async def count_files_in_directory_async(directory):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, count_files_in_directory, directory)


class Anti:
    def __init__(self):
        self.lock = Lock()
        self.partitions = []

    #  Count the total number of files to be scanned
    async def count_files(self, typ):
        if typ == "quick":
            # self.partitions = [
            #     "C:\\Windows\\System32",
            #     "C:\\Program Files",
            #     "C:\\Program Files (x86)",
            #     os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Temp"),
            #     os.path.expandvars("%USERPROFILE%\\AppData\\Roaming"),
            # ]
            self.partitions = [
                r"D:\Treasure of Nadia [FitGirl Repack]"
            ]
        elif typ == "full":
            all_partitions = psutil.disk_partitions()
            for part in all_partitions:
                self.partitions.append(part.device)
            # print(self.partitions)
        else:
            pass

        tasks = [
            count_files_in_directory_async(partition.replace("\\", "/"))
            for partition in self.partitions
        ]
        results = await asyncio.gather(*tasks)

        file_count = sum(results)
        print(f"Total number of files: {file_count}")
        eel.total_files(file_count)
        return file_count

    # Scan directory for viruses
    def scan_directory(self, cd, directory_path):
        eel.remove_raw()
        with ThreadPoolExecutor(
            max_workers=os.cpu_count() * 10
        ) as executor:  # Adjust max_workers based on your CPU
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    executor.submit(self.scan_a_file, cd, file_path)

    # Scan a single file
    def scan_a_file(self, cd, file_path):
        

        try:
            with self.lock:
                eel.current_file(file_path)
                owner = self.get_file_owner(file_path)
                print(owner,self.is_owner_trusted(owner))
                if (owner and self.is_owner_trusted(owner)) or owner == "Administrators":
                    print(f"Skipping {file_path}, owner {owner} is trusted.")
                    return
                # eel.current_file(
                #     os.path.basename(file_path)
                # )  # Change file name on Front-End
                result = cd.scan_file(rf"{file_path}")
                if result is None:
                    print(f"{file_path} is clean")
                else:
                    print(f"Virus found in {file_path}: {result}")
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")

    # //////////////////////////////////
    def get_file_owner(self, file_path):
        """Get the owner of a file (Windows)"""
        try:
            sd = GetFileSecurity(file_path, OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            name, domain, _ = LookupAccountSid(None, owner_sid)
            print(name)
            return name
        except Exception as e:
            print(f"Error getting owner of {file_path}: {e}")
            return None

    def is_owner_trusted(self, owner):
        """Determine if a file owner is a system user (trusted)"""
        # Consider 'SYSTEM', 'Administrator', or 'TrustedInstaller' as trusted
        if owner in ["SYSTEM", "Administrators", "TrustedInstaller"]:
            return True
        else:
            return False


# //////////////////////////////////////


# Function to start the scanning functionalities.
@eel.expose
def start_scan(typ):
    anti = Anti()
    clamd_instance = connect_to_guardium()
    asyncio.run(anti.count_files(typ))
    if clamd_instance:
        for par in anti.partitions:
            anti.scan_directory(clamd_instance, par)


eel.init("web")  # initialize eel


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
