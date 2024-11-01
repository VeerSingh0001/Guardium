import os
import psutil
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from tkinter import Tk, filedialog
import asyncio
import eel
from win32security import GetFileSecurity, OWNER_SECURITY_INFORMATION, LookupAccountSid

class Anti:
    def __init__(self):
        self.lock = Lock()
        self.partitions = []
        self.stop_scan = False

    def __del__(self):
        self.stop_scan = True

    #  Count the total number of files to be scanned
    async def count_files(self, typ):
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
            # print(self.partitions)
        else:
            print("custom")
            root = Tk()
            # root.withdraw()  # Hide the root window
            self.partitions = [filedialog.askdirectory()]
            print("after")

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
        return await loop.run_in_executor(None, self.count_files_in_directory, directory)

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
        # eel.remove_raw()
        with ThreadPoolExecutor(
                max_workers=os.cpu_count() * 10
        ) as executor:
            for root, _, files in os.walk(directory_path):
                if self.stop_scan:
                    # exit(1)
                    break
                for file in files:
                    if self.stop_scan:
                        # exit()
                        break
                    file_path = os.path.join(root, file)
                    executor.submit(self.scan_a_file, cd, file_path)

    # Scan a single file
    def scan_a_file(self, cd, file_path):
        try:
            with self.lock:
                eel.current_file(file_path)
                owner = self.get_file_owner(file_path)
                print(owner, self.is_owner_trusted(owner))
                if (owner and self.is_owner_trusted(owner)) or owner == "Administrators":
                    print(f"Skipping {file_path}, owner {owner} is trusted.")
                    return

                result = cd.scan_file(rf"{file_path}")
                if result is None:
                    print(f"{file_path} is clean")
                else:
                    print(f"Virus found in {file_path}: {result}")
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")

    # Get a file owner
    @staticmethod
    def get_file_owner(file_path):
        """Get the owner of a file (Windows)"""
        try:
            sd = GetFileSecurity(file_path, OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            name, domain, _ = LookupAccountSid(None, owner_sid)
            # print(name)
            return name
        except Exception as e:
            print(f"Error getting owner of {file_path}: {e}")
            return None

    # Check if an owner is trusted or not
    @staticmethod
    def is_owner_trusted(owner):
        """Determine if a file owner is a system user (trusted)"""
        # Consider 'SYSTEM', 'Administrator', or 'TrustedInstaller' as trusted
        if owner in ["SYSTEM", "Administrators", "TrustedInstaller"]:
            return True
        else:
            return False
