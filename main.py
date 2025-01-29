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
key = "BY3VYM-i5pek9UGeijYGvNobJ_sr2yArso6bzwif66E="

@eel.expose
def run_scan(typ):
    global scan_thread
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

@eel.expose
def cancel_scan():
    anti.stop_scan = True
    if anti.executor:
        anti.executor.shutdown(wait=False)
    print("Scan thread has been stopped.")

@eel.expose
def actions(typ, vid, name, file_path, severity, history, category):
    if typ == "remove":
        handle_remove(file_path, history, category)
    elif typ == "allow":
        handle_allow(vid, name, file_path, severity, history)
    elif typ == "restore":
        handle_restore(file_path)
    else:
        handle_quarantine(vid, name, file_path, severity, history, category)

def handle_remove(file_path, history, category):
    if history == "true":
        if category == "allowed":
            data.remove_allowed(file_path)
        else:
            q_path = data.get_quarantined_path(file_path)[0]
            data.remove_quarantined(q_path)
            os.remove(q_path)
    os.remove(file_path)

def handle_allow(vid, name, file_path, severity, history):
    if history == "true":
        q_path = data.get_quarantined_path(file_path)[0]
        restore_file(q_path, file_path)
    data.add_allowed(vid, name, file_path, severity)

def handle_restore(file_path):
    q_path = data.get_quarantined_path(file_path)[0]
    restore_file(q_path, file_path)

def handle_quarantine(vid, name, file_path, severity, history, category):
    if history and category == "allowed":
        data.remove_allowed(file_path)
    fernet = Fernet(key)
    with open(file_path, "rb") as file:
        encrypted_data = fernet.encrypt(file.read())
    quarantine_path = get_unique_quarantine_path(name)
    with open(quarantine_path, "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)
    data.add_quarantine(vid, name, os.path.basename(quarantine_path), file_path, quarantine_path, severity)
    os.remove(file_path)

def get_unique_quarantine_path(name):
    quarantine_path = os.path.join(anti.quarantine_dir, f"{name}.enc")
    counter = 1
    while os.path.exists(quarantine_path):
        quarantine_path = os.path.join(anti.quarantine_dir, f"{counter}_{name}.enc")
        counter += 1
    return quarantine_path

def restore_file(encrypted_file_path, restore_path):
    fernet = Fernet(key)
    with open(encrypted_file_path, "rb") as encrypted_file:
        decrypted_data = fernet.decrypt(encrypted_file.read())
    with open(restore_path, "wb") as restored_file:
        restored_file.write(decrypted_data)
    data.remove_quarantined(encrypted_file_path)
    os.remove(encrypted_file_path)

@eel.expose
def show_allowed():
    allowed_viruses = data.get_all_allowed()
    if not allowed_viruses:
        eel.noVirusFound()
        return
    for virus in allowed_viruses:
        virus_dict = {
            "virus_name": virus.name,
            "virus_path": virus.path,
            "severity": virus.severity,
        }
        eel.showResult(virus_dict, True, "allowed")

@eel.expose
def show_quarantined():
    quarantined_viruses = data.get_all_quarantined()
    if not quarantined_viruses:
        eel.noVirusFound()
        return
    for virus in quarantined_viruses:
        virus_dict = {
            "virus_name": virus.name,
            "virus_path": virus.path,
            "severity": virus.severity,
        }
        eel.showResult(virus_dict, True, "quarantined")

@eel.expose
def update_db():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "powershell.exe",
            f"-Command {os.path.abspath('update.cmd')}",
            None,
            1,
        )
    except Exception as e:
        print(f"Error running .cmd file as Administrator: {e}")

eel.init("web")

screen_reso = pyautogui.size()

try:
    eel.start(
        "index.html",
        port=0,
        mode="chrome",
        size=(screen_reso.width, screen_reso.height),
    )
except EnvironmentError:
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
