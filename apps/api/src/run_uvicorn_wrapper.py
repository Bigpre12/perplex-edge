import sys
import subprocess

with open("uvicorn_crash.txt", "w") as f:
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in iter(process.stdout.readline, ""):
        f.write(line)
        f.flush()
        print(line, end="")
        if "ImportError" in line:
            break
