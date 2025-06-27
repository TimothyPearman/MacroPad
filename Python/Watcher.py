import subprocess
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))                             # get script directory
TARGET_SCRIPT_1 = os.path.join(SCRIPT_DIR, "Data.py")                               # decrlare target scripts
TARGET_SCRIPT_2 = os.path.join(SCRIPT_DIR, "GUI.py")

def start_process(script):
    """Start the target script and return the subprocess object."""
    return subprocess.Popen(["python", script])

process1 = start_process(TARGET_SCRIPT_1)                                           # Start both processes
process2 = start_process(TARGET_SCRIPT_2)

try:                                                                                # Restart if either process dies
    while True:
        if process1.poll() is not None:
            print(f"{TARGET_SCRIPT_1} stopped. Restarting...")
            process1 = start_process(TARGET_SCRIPT_1)
        if process2.poll() is not None:
            print(f"{TARGET_SCRIPT_2} stopped. Restarting...")
            process2 = start_process(TARGET_SCRIPT_2)

        time.sleep(5)

except KeyboardInterrupt:
    print("Stopping both scripts...")
    process1.terminate()
    process2.terminate()
    process1.wait()
    process2.wait()
