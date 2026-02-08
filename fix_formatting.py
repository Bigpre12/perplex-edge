#!/usr/bin/env python3
"""
Fix common formatting issues in API files
"""
import os
import re

def fix_file(filepath):
    """Fix formatting issues in a single file"""
    fixed = False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix double spaces
        content = re.sub(r'  +', ' ', content)
        
        # Fix trailing spaces
        content = re.sub(r' +\n', '\n', content)
        
        # Fix multiple consecutive newlines (more than 2)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Fix space before opening parenthesis
        content = re.sub(r'(\w)\s*\(', r'\1(', content)
        
        # Fix space after opening parenthesis
        content = re.sub(r'\(\s+', '(', content)
        
        # Fix space before closing parenthesis
        content = re.sub(r'\s+\)', ')', content)
        
        # Fix space around operators (ensure single space)
        content = re.sub(r' *= *', ' = ', content)
        content = re.sub(r' *\+ *', ' + ', content)
        content = re.sub(r' *- *', ' - ', content)
        content = re.sub(r' *\* *', ' * ', content)
        content = re.sub(r' */ *', ' / ', content)
        
        # Remove unneeded words
        unneeded_words = ['basically ', 'actually ', 'literally ', 'really ', 'very ', 
                         'quite ', 'rather ', 'pretty ', 'just ', 'simply ', 'merely ']
        for word in unneeded_words:
            content = re.sub(rf'\b{re.escape(word.strip())}\b', '', content, flags=re.IGNORECASE)
        
        # Remove redundant phrases
        redundant_phrases = ['in order to ', 'due to the fact that ', 'as a matter of fact ']
        for phrase in redundant_phrases:
            content = re.sub(rf'\b{re.escape(phrase.strip())}\b', '', content, flags=re.IGNORECASE)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed = True
    
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    
    return fixed

def main():
    """Fix all files"""
    api_dir = "backend/app/api"
    files_fixed = 0
    
    print("FIXING FORMATTING ISSUES")
    print("="*80)
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                if fix_file(filepath):
                    files_fixed += 1
                    rel_path = os.path.relpath(filepath, api_dir)
                    print(f"Fixed: {rel_path}")
    
    print(f"\n{'='*80}")
    print(f"FIXING COMPLETE")
    print(f"Files fixed: {files_fixed}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
