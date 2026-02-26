import os

INPUT_FILE = "perplex_engine_full_context.md"
CHUNK_SIZE_LINES = 15000  # Approx 500-800KB depending on line length, safe for copy-paste
OUTPUT_PREFIX = "perplex_context_part_"

def split_file():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines: {total_lines}")

    chunk_num = 1
    for i in range(0, total_lines, CHUNK_SIZE_LINES):
        chunk_lines = lines[i:i + CHUNK_SIZE_LINES]
        output_filename = f"{OUTPUT_PREFIX}{chunk_num}.md"
        
        with open(output_filename, 'w', encoding='utf-8') as out:
            # Add a header to each part context
            out.write(f"# Part {chunk_num} of Perplex Engine Context\n\n")
            out.writelines(chunk_lines)
            
        print(f"Created {output_filename} ({len(chunk_lines)} lines)")
        chunk_num += 1

if __name__ == "__main__":
    split_file()
