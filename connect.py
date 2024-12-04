import os
import subprocess

import pyclamd


class Connect:
    def __init__(self):
        self.cd = None

    # Connect to the ClamAV daemon
    def connect_to_guardium(self):
        try:
            self.cd = pyclamd.ClamdNetworkSocket()  # Use network socket connection
            if self.cd.ping():
                print("Connected to Guardium daemon")
                return self.cd
            else:
                print("Failed to connect to Guardium daemon")
                cmd_file_path = os.path.abspath("service.cmd")
                res = self.run_cmd_as_admin(cmd_file_path)
                # eel.alertUser()
                if res : return self.cd
                return None
        except pyclamd.ConnectionError:
            print("Could not connect to Guardium daemon.")
            cmd_file_path = os.path.abspath("service.cmd")
            res  = self.run_cmd_as_admin(cmd_file_path)
            # eel.alertUser()
            if res : return self.cd
            return None

    @staticmethod
    def run_cmd_as_admin(cmd_file_path):
        """Run a .cmd file with Administrator privileges using PowerShell."""
        try:
            # ctypes.windll.shell32.ShellExecuteW(
            #     None,
            #     "runas",  # Request admin privileges
            #     "powershell.exe",  # PowerShell executable
            #     f"-Command {cmd_file_path}",  # Pass the .cmd file path
            #     None,
            #     1,  # Show a new console window
            # )
            command = f'powershell -Command "Start-Process \\"cmd.exe\\" -ArgumentList \\"/c {cmd_file_path}\\" -Verb RunAs"'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("CMD file executed successfully.")
                return True
            else:
                print(f"Error: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error running .cmd file as Administrator: {e}")
            return None

