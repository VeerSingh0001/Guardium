import ctypes

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
run_cmd_as_admin(r"D:\Github_Repos\Guardium\update.cmd")
