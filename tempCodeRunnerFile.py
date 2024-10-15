import subprocess

from elevate import elevate

elevate()

# startupinfo = subprocess.STARTUPINFO()
# startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

# Run the .cmd file without showing the console window
# process = subprocess.Popen(
#     ["cmd.exe", "/c", r"service.cmd"],  # Full or relative path to your .cmd file
#     stdout=subprocess.PIPE,  # Redirect stdout
#     stderr=subprocess.PIPE,  # Redirect stderr
#     startupinfo=startupinfo,  # Use the startup info to hide window
#     creationflags=subprocess.CREATE_NO_WINDOW  # Don't show console window
# )

print("Starting")
result = subprocess.run(["cmd.exe", "/c", r"service.cmd"], shell=True)
print("Started")
print(result.stderr)
print(result.stdout)
