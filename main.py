import asyncio
import platform
import sys
import threading

import eel
import pyautogui

from anti import Anti
from connect import Connect

anti = Anti()


# Function to start the scanning functionalities.
@eel.expose
def run_scan(typ):
    global anti
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
            anti.scan_directory(guardium_instance, par)


@eel.expose
def cancel_scan():
    global anti
    anti.stop_scan = True


@eel.expose
def show_result():
    global anti
    eel.showResult(anti.virus_results)
    # print(anti.virus_results[0])


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
