import asyncio
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
        for par in anti.partitions:
            if anti.stop_scan:
                print("Scan canceled mid-process.")
                break  # Exit if scan canceled

            anti.scan_directory(guardium_instance, par)
    print("Scan finished or canceled.")
    eel.update_interface()


@eel.expose
def cancel_scan():
    global anti, scan_thread
    # if scan_thread and scan_thread.is_alive():
    anti.stop_scan = True  # Signal the thread to stop
    #     scan_thread.join()  # Wait for the scan thread to exit
    if anti.executor:
        anti.executor.shutdown(wait=False)
    print("Scan thread has been stopped.")


@eel.expose
def actions(typ, vid, name, file_path, severity):
    global anti
    # file_path.replace("\\", "\\")
    print(file_path)
    if typ == "remove":
        os.remove(file_path)
    elif typ == "allow":
        data.add_allowed(vid, name, file_path, severity)
    else:
        # Load the encryption key
        with open("key.key", "rb") as key_file:
            key = key_file.read()
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

        # quarantine_path = os.path.join(anti.quarantine_dir, name)
        # quarantine_name = name
        # counter = 1
        # while os.path.exists(quarantine_path):
        #     quarantine_path = os.path.join(anti.quarantine_dir, f"{counter}_{name}")
        #     quarantine_name = f"{counter}_{name}"
        #     counter += 1
        #
        # data.add_quarantine(vid, name, quarantine_name, file_path, quarantine_path, severity)
        #
        # shutil.move(file_path, quarantine_path)
        # print(f"File quarantined: {quarantine_path}")


@eel.expose
def show_allowed():
    # Fetch and display all records in the `allowed` table
    allowed_viruses = data.get_all_allowed()
    for virus in allowed_viruses:
        print(f"ID: {virus.id}, Name: {virus.name}, Path: {virus.path}, Severity: {virus.severity}")


@eel.expose
def show_quarantined():
    quarantined_viruses = data.get_all_quarantined()
    for virus in quarantined_viruses:
        print(f"ID: {virus.id}, Name: {virus.name}, Path: {virus.path}, Severity: {virus.severity}")


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
    sys.exit(0)
