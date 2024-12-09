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
def actions(typ, vid, name, file_path, severity, history, catorgry):
    global anti
    key = "BY3VYM-i5pek9UGeijYGvNobJ_sr2yArso6bzwif66E="

    if typ == "remove":
        print(file_path)
        print(history)
        if history:
            print(catorgry)
            if catorgry == "allowed":
                data.remove_allowed(file_path)
                os.remove(file_path)
            else:
                q_path = data.get_quarantined_path(file_path)[0]
                print(f"Quarantined file path: {q_path}")
                data.remove_quarantined(q_path)
                os.remove(q_path)
        else:
            os.remove(file_path)
    elif typ == "allow":
        if history:
            q_path = data.get_quarantined_path(file_path)[0]
            restore_file(q_path, file_path, key)
            data.add_allowed(vid, name, file_path, severity)
        else:
            data.add_allowed(vid, name, file_path, severity)
    elif typ == "restore":
        q_path = data.get_quarantined_path(file_path)[0]
        restore_file(q_path, file_path, key)

    else:
        if history and catorgry == "allowed":
            data.remove_allowed(file_path)
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
        os.remove(file_path)


def restore_file(encrypted_file_path, restore_path, key):
    fernet = Fernet(key)

    # Read the encrypted file
    with open(encrypted_file_path, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    # Decrypt the data
    decrypted_data = fernet.decrypt(encrypted_data)

    # Save the decrypted file
    with open(restore_path, "wb") as restored_file:
        restored_file.write(decrypted_data)

    print(f"File decrypted and restored to {restore_path}")
    print(f"Encrypted file path: {encrypted_file_path}")
    data.remove_quarantined(encrypted_file_path)
    os.remove(encrypted_file_path)


# To get all allowed threats
@eel.expose
def show_allowed():
    # Fetch and display all records in the `allowed` table
    allowed_viruses = data.get_all_allowed()
    eel.clearTable()
    for virus in allowed_viruses:
        virus_dict = {
            "virus_name": virus.name,
            "virus_path": virus.path,
            "severity": virus.severity,
        }
        eel.showResult(virus_dict, True, "allowed")


# To get all quarantine threats
@eel.expose
def show_quarantined():
    quarantined_viruses = data.get_all_quarantined()
    eel.clearTable()
    for virus in quarantined_viruses:
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
