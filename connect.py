import pyclamd,subprocess,ctypes,sys


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
                return None
        except pyclamd.ConnectionError:
            print("Could not connect to Guardium daemon.")
            # subprocess.run(f'runas /user:Administrator "net start clamd"', shell=True)
            self.run_as_admin()
            return None

    @staticmethod
    def run_as_admin():
        if ctypes.windll.shell32.IsUserAnAdmin():
            # The script has admin privileges
            # Place the command you want to run here
            subprocess.run("service.cmd", shell=True)
        else:
            # Request admin privileges
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

    # run_as_admin()