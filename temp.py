from concurrent.futures import ThreadPoolExecutor
import os
from threading import Lock
import eel

class Anti:
    def __init__(self):
        self.lock = Lock()
        self.partitions = []
        self.stop_scan = False
        self.virus_results = []
        self.executor = None  # To store ThreadPoolExecutor reference

    # Function to cancel scanning
    @eel.expose
    def cancel_scan(self):
        self.stop_scan = True
        if self.executor:
            self.executor.shutdown(wait=False)  # Attempt to stop threads immediately
        print("Scan canceled.")

    # Scanning method with check for stop_scan flag
    def scan_directory(self, cd, directory_path):
        # Use executor for managing threads
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count() * 10)
        for root, _, files in os.walk(directory_path):
            if self.stop_scan:  # Check stop_scan at directory level
                break
            for file in files:
                if self.stop_scan:  # Check stop_scan at file level
                    break
                file_path = os.path.join(root, file)
                self.executor.submit(self.scan_a_file, cd, file_path)

        self.executor.shutdown(wait=True)  # Wait for remaining threads to complete if not canceled

    # Scan individual file with stop_scan check
    def scan_a_file(self, cd, file_path):
        if self.stop_scan:  # Exit immediately if stop_scan is set
            return
        try:
            with self.lock:
                eel.current_file(file_path)
                owner = self.get_file_owner(file_path)
                if owner and self.is_owner_trusted(owner):
                    return

                result = cd.scan_file(rf"{file_path}")
                if result:
                    virus_name = os.path.basename(file_path)
                    severity = self.determine_severity(virus_name)
                    self.virus_results.append({'virus_name': virus_name, 'severity': severity})
                    print(f"Virus found in {file_path}: {result}")
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
