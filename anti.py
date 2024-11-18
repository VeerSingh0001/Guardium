import asyncio
import os
import subprocess
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
        self.total_viruses = 0  # List to store virus scan results
        self.executor = None
        self.quarantine_dir = r"C:\Guardium\Quarantine"
        if not os.path.exists(self.quarantine_dir):
            os.makedirs(self.quarantine_dir, exist_ok=True)

    # @eel.expose
    # def stop_scan(self):
    #     self.stop_scan = True
    #     if self.executor:
    #         self.executor.shutdown(wait=False)

    #  Count the total number of files to be scanned
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
            for part in all_partitions:
                self.partitions.append(part.device)
        else:
            root = Tk()
            dirct = filedialog.askdirectory().replace("/", "\\")
            root.destroy()
            self.partitions.append(dirct)

        tasks = [
            self.count_files_in_directory_async(partition.replace("\\", "/"))
            for partition in self.partitions
        ]
        results = await asyncio.gather(*tasks)

        file_count = sum(results)
        print(f"Total number of files: {file_count}")
        eel.total_files(file_count)
        return file_count

    async def count_files_in_directory_async(self, directory):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.count_files_in_directory, directory
        )

    # Count the total files number in the directory
    @staticmethod
    def count_files_in_directory(directory):
        file_count = 0
        try:
            for _, _, files in os.walk(directory):
                file_count += len(files)
        except Exception as e:
            print(f"Error counting files in {directory}: {e}")
        return file_count

    # Scan directory for viruses
    def scan_directory(self, cd, directory_path):
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count() * 4)
        for root, _, files in os.walk(directory_path):
            if self.stop_scan:  # Exit if scanning was canceled
                print("Exiting scan_directory early due to cancel request.")
                break
                # return
            for file in files:
                if self.stop_scan:  # Exit if scanning was canceled
                    print("Exiting scan_directory early due to cancel request.")
                    break
                    # return
                file_path = os.path.join(root, file)
                self.executor.submit(self.scan_a_file, cd, file_path)
        self.executor.shutdown(wait=True)

    # Scan a single file
    def scan_a_file(self, cd, file_path):
        if self.stop_scan:
            return  # Exit if scanning was canceled
        try:
            with self.lock:
                eel.current_file(file_path)
                owner = self.get_file_owner(file_path)
                if owner and self.is_owner_trusted(owner):
                    return

                result = cd.scan_file(rf"{file_path}")
                if result and isinstance(result, dict) and file_path in result and result[file_path][0] == 'FOUND':
                    file_exists = data.check_path_exists(file_path)
                    if file_exists:
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
                    eel.showResult(virus_dict)
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")

    # Get a file owner
    @staticmethod
    def get_file_owner(file_path):
        try:
            sd = GetFileSecurity(file_path, OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            name, domain, _ = LookupAccountSid(None, owner_sid)
            return name
        except Exception as e:
            print(f"Error getting owner of {file_path}: {e}")
            return None

    # Check if an owner is trusted or not
    @staticmethod
    def is_owner_trusted(owner):
        if owner in ["SYSTEM", "TrustedInstaller"]:
            return True
        else:
            return False

    # Determine the severity based on virus name
    @staticmethod
    def determine_severity(result, path):
        if any(
                keyword in (str(result[path][1]).lower())
                for keyword in ["trojan", "worm", "malware"]
        ):
            return "High"
        elif "adware" in str(result[path][1]).lower():
            return "Medium"
        else:
            return "Low"
