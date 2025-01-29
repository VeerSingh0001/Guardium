import ctypes
import sys
import subprocess
import shutil
import os
import tempfile

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def stop_and_delete_service(service_name):
    try:
        # Stop the service
        subprocess.run(['sc', 'stop', service_name], check=True)
        print(f"Service {service_name} stopped successfully.")
        
        # Delete the service
        subprocess.run(['sc', 'delete', service_name], check=True)
        print(f"Service {service_name} deleted successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop or delete service {service_name}: {e}")

def delete_folder(folder_path):
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Folder {folder_path} deleted successfully.")
        else:
            print(f"Folder {folder_path} does not exist.")
    except Exception as e:
        print(f"Failed to delete folder {folder_path}: {e}")

def create_deletion_batch(script_path, current_folder):
    batch_content = f"""
    @echo off
    timeout /t 2 /nobreak > NUL
    del "{script_path}"
    rmdir /s /q "{current_folder}"
    """
    batch_file = os.path.join(tempfile.gettempdir(), "delete_script.bat")
    with open(batch_file, "w") as f:
        f.write(batch_content)
    return batch_file

if __name__ == "__main__":
    if is_admin():
        service_name = "clamd"  # Replace with your service name
        stop_and_delete_service(service_name)
        
        folder_path = r"C:\Guardium"  # Replace with your folder path
        delete_folder(folder_path)
        
        # Delete the current script file and folder
        script_path = os.path.abspath(__file__)
        current_folder = os.path.dirname(script_path)
        
        batch_file = create_deletion_batch(script_path, current_folder)
        subprocess.Popen(["cmd", "/c", batch_file])
    else:
        # Re-run the script with admin privileges
        print("Requesting administrative privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)