import os
import pyclamd


# Connect to the ClamAV daemon
def connect_to_clamd():
    try:
        cd = pyclamd.ClamdNetworkSocket()  # Use network socket connection
        if cd.ping():
            print("Connected to ClamAV daemon")
            return cd
        else:
            print("Failed to connect to ClamAV daemon")
            return None
    except pyclamd.ConnectionError:
        print("Could not connect to ClamAV daemon.")
        return None


# Scan a directory
def scan_directory(cd, directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = fr"{os.path.join(root, file)}"
            scan_file(cd, file_path)


# Scan a single file
def scan_file(cd, file_path):
    try:
        result = cd.scan_file(file_path)
        if result is None:
            print(f"{file_path} is clean")
        else:
            print(f"Virus found in {file_path}: {result}")
    except Exception as e:
        print(f"Error scanning file {file_path}: {e}")


# Example usage
if __name__ == "__main__":
    directory_to_scan = r"D:\\"  # Replace with the directory you want to scan

    # Connect to ClamAV
    clamd_instance = connect_to_clamd()

    if clamd_instance:
        # Scan the directory
        scan_directory(clamd_instance, directory_to_scan)
