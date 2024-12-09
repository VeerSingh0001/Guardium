import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from tkinter import Tk, filedialog

import eel
import psutil
from win32security import GetFileSecurity, OWNER_SECURITY_INFORMATION, LookupAccountSid

from database import Data

data = Data()


class Anti:
    def __init__(self):
        self.lock = Lock()
        self.partitions = []
        self.stop_scan = False
        self.total_viruses = 0
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count() * 8)
        self.quarantine_dir = r"C:\Guardium\Quarantine"
        if not os.path.exists(self.quarantine_dir):
            os.makedirs(self.quarantine_dir, exist_ok=True)

    # Count the total number of files
    async def count_files(self, typ):
        self.partitions = []
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
            self.partitions = [part.device for part in all_partitions]
        else:
            root = Tk()
            dirct = filedialog.askdirectory().replace("/", "\\")
            root.destroy()
            self.partitions.append(dirct)

        tasks = [self.count_files_in_directory_async(part.replace("\\", "/")) for part in self.partitions]
        results = await asyncio.gather(*tasks)

        file_count = sum(results)
        print(f"Total number of files: {file_count}")
        eel.total_files(file_count)
        return file_count

    async def count_files_in_directory_async(self, directory):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.count_files_in_directory, directory)

    @staticmethod
    def count_files_in_directory(directory):
        file_count = 0
        try:
            for _, _, files in os.walk(directory):
                file_count += len(files)
        except Exception as e:
            print(f"Error counting files in {directory}: {e}")
        return file_count

    # Scan a directory
    async def scan_directory(self, cd, directory_path):
        loop = asyncio.get_event_loop()
        tasks = []
        for root, _, files in os.walk(directory_path):
            if self.stop_scan:
                print("Exiting scan_directory early due to cancel request.")
                break
            for file in files:
                if self.stop_scan:
                    print("Exiting scan_directory early due to cancel request.")
                    break
                file_path = os.path.join(root, file)
                tasks.append(loop.run_in_executor(None, self.scan_a_file, cd, file_path))
        await asyncio.gather(*tasks)

    # Scan a file
    def scan_a_file(self, cd, file_path):
        if self.stop_scan:
            return
        try:
            with self.lock:
                eel.current_file(file_path)
                owner = self.get_file_owner(file_path)
                if owner and self.is_owner_trusted(owner):
                    return

                result = cd.scan_file(rf"{file_path}")
                if result and isinstance(result, dict) and file_path in result and result[file_path][0] == 'FOUND':
                    if data.check_path_exists(file_path):
                        print("File exists")
                        return
                    self.total_viruses += 1
                    virus_name = os.path.basename(file_path)
                    severity = self.determine_severity(result, file_path)
                    virus_dict = {
                        "virus_name": virus_name,
                        "virus_path": file_path,
                        "severity": severity,
                    }
                    eel.showResult(virus_dict, False)
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")

    # Get a file owner
    @staticmethod
    def get_file_owner(file_path):
        try:
            sd = GetFileSecurity(file_path, OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            name, _, _ = LookupAccountSid(None, owner_sid)
            return name
        except Exception as e:
            print(f"Error getting owner of {file_path}: {e}")
            return None

    # Check owner is trusted or not
    @staticmethod
    def is_owner_trusted(owner):
        return owner in ["SYSTEM", "TrustedInstaller"]

    # Check the severity of the threat
    @staticmethod
    def determine_severity(result, path):
        if any(keyword in (str(result[path][1]).lower()) for keyword in ["trojan", "worm", "malware"]):
            return "High"
        elif "adware" in str(result[path][1]).lower():
            return "Medium"
        else:
            return "Low"
