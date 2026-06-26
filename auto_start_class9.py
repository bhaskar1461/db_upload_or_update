import subprocess
import time
import sys

def check_uploaders_running():
    # Query Win32_Process using powershell
    cmd = 'powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*selenium_uploader_6to9.py*classes*\' } | Select-Object CommandLine"'
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        for line in output.splitlines():
            # Check if class 6, 7, or 8 uploader is active
            if any(f'classes {c}' in line or f'--classes {c}' in line for c in ['6', '7', '8']):
                return True
        return False
    except Exception as e:
        # If CIM fails, fallback to tasklist check
        try:
            tasklist_out = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe" /FO LIST', shell=True, text=True)
            # If we fail, we assume true to be safe
            return True
        except:
            return True

print("Watcher started. Monitoring Class 6, 7, and 8 uploaders...", flush=True)
while True:
    if not check_uploaders_running():
        print("Classes 6, 7, and 8 uploaders have finished!", flush=True)
        break
    time.sleep(60)

print("Launching Class 9 uploader...", flush=True)
subprocess.Popen('python -X utf8 selenium_uploader_6to9.py --classes 9', shell=True)
print("Class 9 uploader launched successfully. Watcher exiting.", flush=True)
