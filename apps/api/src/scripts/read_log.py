import os

log_file = "sync_debug.log"
if not os.path.exists(log_file):
    print(f"File {log_file} not found")
else:
    # Try reading with different encodings
    for enc in ['utf-16', 'utf-8', 'cp1252']:
        try:
            with open(log_file, "r", encoding=enc) as f:
                content = f.read()
                print(f"--- Encoding: {enc} ---")
                lines = content.splitlines()
                # Find lines with "ERROR" or "Exception"
                for i, line in enumerate(lines):
                    if "ERROR" in line or "Exception" in line or "fail" in line.lower():
                        # Print context
                        start = max(0, i - 3)
                        end = min(len(lines), i + 10)
                        for j in range(start, end):
                            print(f"{j+1}: {lines[j]}")
                        print("-" * 20)
                break
        except UnicodeDecodeError:
            continue
