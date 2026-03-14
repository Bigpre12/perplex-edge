import subprocess
import sys
import os

# Get the absolute path to the apps/api directory
api_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps", "api")

# Change to the api directory
os.chdir(api_dir)

# Ensure the virtual environment is used if it exists in the root
venv_python = os.path.join(os.path.dirname(api_dir), "..", ".venv", "Scripts", "python.exe")
python_exe = venv_python if os.path.exists(venv_python) else sys.executable

print(f"--- Starting Lucrix API from {api_dir} ---")

# Run the backend run_api.py
try:
    subprocess.run([python_exe, "run_api.py"], env={**os.environ, "PORT": "8000"})
except KeyboardInterrupt:
    print("\n--- Stopping API ---")
except Exception as e:
    print(f"Error starting API: {e}")
