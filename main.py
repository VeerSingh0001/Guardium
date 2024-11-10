import asyncio
import platform
import sys
import threading

import eel
import pyautogui

from anti import Anti
from connect import Connect

anti = Anti()
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
                break  # Exit if scan is canceled

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
def show_result():
    global anti
    eel.showResult(anti.total_viruses)


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
