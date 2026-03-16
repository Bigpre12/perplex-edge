import sys
import traceback

sys.path.append('apps/api/src')
try:
    import main
    with open('full_error.txt', 'w') as f:
        f.write('SUCCESS')
except Exception as e:
    with open('full_error.txt', 'w') as f:
        traceback.print_exc(file=f)
