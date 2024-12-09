import asyncio
import ctypes
import os
import platform
import sys
import threading

import eel
import pyautogui
from cryptography.fernet import Fernet

from anti import Anti
from connect import Connect
from database import Data

anti = Anti()
data = Data()
scan_thread = None

# Function to start the scanning functionalities.
@eel.expose
def run_scan(typ):
    global anti, scan_thread
    anti.stop_scan = False
    scan_thread = threading.Thread(target=start_scan, args=(typ,))
    scan_thread.start()

def start_scan(typ):
    anti.virus_results = []
    conn = Connect()
    guardium_instance = conn.connect_to_guardium()

    asyncio.run(anti.count_files(typ))

    if guardium_instance:
        asyncio.run(scan_all_directories(guardium_instance, anti.partitions))
    print("Scan finished or canceled.")
    eel.update_interface()

async def scan_all_directories(cd, partitions):
    tasks = [anti.scan_directory(cd, par) for par in partitions]
    await asyncio.gather(*tasks)

# To cancel a running scan
@eel.expose
def cancel_scan():
    global anti
    anti.stop_scan = True  # Signal the thread to stop

    if anti.executor:
        anti.executor.shutdown(wait=False)
    print("Scan thread has been stopped.")

# To perform remove, quarantine or allow action on detected threats
@eel.expose
def actions(typ, vid, name, file_path, severity):
    global anti
    print(file_path)
    key = "BY3VYM-i5pek9UGeijYGvNobJ_sr2yArso6bzwif66E="
    if typ == "remove":
        os.remove(file_path)
    elif typ == "allow":
        data.add_allowed(vid, name, file_path, severity)
    else:
        fernet = Fernet(key)

        # Read the file contents
        with open(file_path, "rb") as file:
            file_data = file.read()

        # Encrypt the data
        encrypted_data = fernet.encrypt(file_data)

        quarantine_path = os.path.join(anti.quarantine_dir, f"{name}.enc")
        quarantine_name = name
        counter = 1
        while os.path.exists(quarantine_path):
            quarantine_path = os.path.join(anti.quarantine_dir, f"{counter}_{name}.enc")
            quarantine_name = f"{counter}_{name}"
            counter += 1

        with open(quarantine_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)

        print(f"File encrypted and stored at {quarantine_path}")

        data.add_quarantine(vid, name, quarantine_name, file_path, quarantine_path, severity)

# To get all allowed threats
@eel.expose
def show_allowed():
    # Fetch and display all records in the `allowed` table
    allowed_viruses = data.get_all_allowed()
    for virus in allowed_viruses:
        # print(f"ID: {virus.id}, Name: {virus.name}, Path: {virus.path}, Severity: {virus.severity}")
        virus_dict = {
            "virus_name": virus.name,
            "virus_path": virus.path,
            "severity": virus.severity,
        }
        eel.showResult(virus_dict,True,"allowed")
    # print(viruses_list)
    # return  viruses_list

# To get all quarantine threats
@eel.expose
def show_quarantined():
    quarantined_viruses = data.get_all_quarantined()
    for virus in quarantined_viruses:
        # print(f"ID: {virus.id}, Name: {virus.name}, Path: {virus.path}, Severity: {virus.severity}")
        virus_dict = {
            "virus_name": virus.name,
            "virus_path": virus.path,
            "severity": virus.severity,
        }
        eel.showResult(virus_dict, True, "quarantined")

# Update antivirus signature database
@eel.expose
def update_db():
    """Run a .cmd file with Administrator privileges using PowerShell."""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # Request admin privileges
            "powershell.exe",  # PowerShell executable
            f"-Command {os.path.abspath('update.cmd')}",  # Pass the .cmd file path
            None,
            1,  # Show a new console window
        )
    except Exception as e:
        print(f"Error running .cmd file as Administrator: {e}")

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
    # If Chrome not found, fallback to Microsoft Edge on Win10 or greater
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
    cancel_scan()
    sys.exit(0)

