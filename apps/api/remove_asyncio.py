import os

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()

    if 'sqlalchemy.ext.asyncio' not in data:
        return

    print(f"Adapting {path} ...")
    lines = data.split('\n')
    new_lines = []
    has_async_import = False
    
    for line in lines:
        if 'from sqlalchemy.ext.asyncio import' in line:
            has_async_import = True
            continue  # Drop this line
        new_lines.append(line)
        
    if has_async_import:
        # Provide a dummy class so type hints don't crash
        new_lines.insert(0, "class AsyncSession: pass")

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))

print("DONE.")
