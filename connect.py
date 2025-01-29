import os
import subprocess
import pyclamd

class Connect:
    def __init__(self):
        self.cd = None

    def connect_to_guardium(self):
        try:
            self.cd = pyclamd.ClamdNetworkSocket()
            if self.cd.ping():
                print("Connected to Guardium daemon")
                return self.cd
            else:
                return self._attempt_reconnect()
        except pyclamd.ConnectionError:
            return self._attempt_reconnect()

    def _attempt_reconnect(self):
        print("Could not connect to Guardium daemon.")
        cmd_file_path = os.path.abspath("service.cmd")
        if self.run_cmd_as_admin(cmd_file_path):
            return self.cd
        return None

    @staticmethod
    def run_cmd_as_admin(cmd_file_path):
        try:
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
