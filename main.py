import asyncio
import eel
import platform
import pyautogui
import sys
from connect import Connect
from anti import Anti

anti = None
# Function to start the scanning functionalities.
@eel.expose
def start_scan(typ):
    global anti
    conn = Connect()
    guardium_instance = conn.connect_to_guardium()
    anti = Anti()

    asyncio.run(anti.count_files(typ))
    if guardium_instance:
        for par in anti.partitions:
            anti.scan_directory(guardium_instance, par)


@eel.expose
def cancel_scanning():
    global anti
    print("Stopping scan")
    eel.logging("Stopping scan")
    del anti
    anti = None


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
