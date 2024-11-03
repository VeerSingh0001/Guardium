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
                return None
        except pyclamd.ConnectionError:
            print("Could not connect to Guardium daemon.")
            return None
