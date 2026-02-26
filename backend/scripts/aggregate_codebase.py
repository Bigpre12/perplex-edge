import os

# Configuration
OUTPUT_FILE = "perplex_engine_full_context.md"
ROOT_DIR = "."
INCLUDED_EXTENSIONS = {".py", ".html", ".css", ".js", ".md"}
EXCLUDED_DIRS = {".git", "__pycache__", "venv", ".gemini", ".antigravity", "node_modules", ".agent"}
EXCLUDED_FILES = {
    "perplex_engine_full_context.md", 
    "ai_studio_context.md",
    "aggregate_codebase.py", 
    "poetry.lock", 
    "package-lock.json",
    "Pipfile.lock"
}
DOC_FILES = [
    r"C:\Users\preio\.gemini\antigravity\brain\23031bcc-5d90-44ed-b394-f641bed90f74\task.md",
    r"C:\Users\preio\.gemini\antigravity\brain\23031bcc-5d90-44ed-b394-f641bed90f74\implementation_plan.md",
    r"C:\Users\preio\.gemini\antigravity\brain\23031bcc-5d90-44ed-b394-f641bed90f74\walkthrough.md"
]

def is_source_file(filename):
    return any(filename.endswith(ext) for ext in INCLUDED_EXTENSIONS) and filename not in EXCLUDED_FILES

def get_file_content(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        outfile.write("# Perplex Engine - Complete Context for AI\n\n")

        # 0. Prepend Documentation
        for doc_path in DOC_FILES:
            if os.path.exists(doc_path):
                content = get_file_content(doc_path)
                filename = os.path.basename(doc_path)
                outfile.write(f"## Documentation: {filename}\n\n")
                outfile.write(content)
                outfile.write("\n\n---\n\n")

        # 1. Root Files
        for item in os.listdir(ROOT_DIR):
            if os.path.isfile(item) and is_source_file(item):
                 write_file_section(outfile, item, item)

        # 2. App Directory (Frontend)
        walk_and_write(outfile, "app")
        
        # 3. Backend Directory
        walk_and_write(outfile, "backend")

        # 4. Static Directory
        if os.path.exists("static"): 
             walk_and_write(outfile, "static")

    print(f"Successfully generated {OUTPUT_FILE}")

def walk_and_write(outfile, start_dir):
    if not os.path.exists(start_dir):
        return

    for root, dirs, files in os.walk(start_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            if is_source_file(file):
                filepath = os.path.join(root, file)
                # Normalize path separators
                rel_path = filepath.replace("\\", "/")
                write_file_section(outfile, filepath, rel_path)

def write_file_section(outfile, filepath, rel_path):
    content = get_file_content(filepath)
    ext = os.path.splitext(filepath)[1][1:] # removing dot
    if ext == "md": ext = "markdown"
    
    outfile.write(f"## File: {rel_path}\n")
    outfile.write(f"```{ext}\n")
    outfile.write(content)
    outfile.write("\n```\n\n")

if __name__ == "__main__":
    main()
