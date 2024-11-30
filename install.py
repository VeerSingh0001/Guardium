import ctypes
import os
import shutil
import tarfile

# Path to your .tar.gz file
file_path = "Guardium.tar.gz"
# Destination directory to extract to
extract_to = r"."

source = rf"{os.getcwd()}\Guardium"
destination = r"C:"

try:
    # Open the .tar.gz file
    with tarfile.open(file_path, "r:gz") as tar:
        print("Extracting files...")
        tar.extractall(path=extract_to, filter=None)  # Explicitly set filter to None
        print(f"Files extracted to: {extract_to}")


except FileNotFoundError:
    print(f"The file {file_path} was not found.")
except tarfile.TarError as e:
    print(f"Error processing the tar.gz file: {e}")

try:
    # Move the directory
    shutil.move(source, destination)
    print(f"Directory moved from {source} to {destination}")
except FileNotFoundError:
    print("The source directory does not exist.")
except PermissionError:
    print("Permission denied.")
except Exception as e:
    print(f"An error occurred: {e}")

def run_cmd_as_admin(cmd_file_path):
    """Run a .cmd file with Administrator privileges using PowerShell."""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # Request admin privileges
            "powershell.exe",  # PowerShell executable
            f"-Command {cmd_file_path}",  # Pass the .cmd file path
            None,
            1,  # Show a new console window
        )
    except Exception as e:
        print(f"Error running .cmd file as Administrator: {e}")

# Example: Provide the full path to your .cmd file
abs_path = os.path.abspath("install.cmd")
run_cmd_as_admin(abs_path)




