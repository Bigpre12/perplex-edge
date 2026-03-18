import sys
import traceback

try:
    sys.path.append('.')
    import main
    print("main.app imported successfully")
except Exception as e:
    with open("crash_verbose.txt", "w") as f:
        traceback.print_exc(file=f)
