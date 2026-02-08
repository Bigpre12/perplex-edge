#!/usr/bin/env python3
"""
Comprehensive search for misspellings, unneeded words, and code blocks
"""
import os
import re
from collections import defaultdict

# Common misspellings (excluding valid words like tomorrow, weather, yesterday, personal)
COMMON_MISSPELLINGS = {
    'definately': 'definitely',
    'occured': 'occurred',
    'occurence': 'occurrence',
    'recieve': 'receive',
    'seperate': 'separate',
    'untill': 'until',
    'wich': 'which',
    'thier': 'their',
    'begining': 'beginning',
    'comming': 'coming',
    'happend': 'happened',
    'knowlege': 'knowledge',
    'maintainance': 'maintenance',
    'neccessary': 'necessary',
    'paralell': 'parallel',
    'prefered': 'preferred',
    'refering': 'referring',
    'relevent': 'relevant',
    'repetetive': 'repetitive',
    'sincerly': 'sincerely',
    'sucess': 'success',
    'supercede': 'supersede',
    'temperture': 'temperature',
    'tendancy': 'tendency',
    'transfered': 'transferred',
    'usally': 'usually',
    'writting': 'writing',
    'paramater': 'parameter',
    'paramaters': 'parameters',
    'endpont': 'endpoint',
    'endponts': 'endpoints',
    'responce': 'response',
    'requst': 'request',
    'requsts': 'requests',
    'authenication': 'authentication',
    'authorzation': 'authorization',
    'conection': 'connection',
    'databse': 'database',
    'databses': 'databases',
    'excecute': 'execute',
    'funtion': 'function',
    'funtions': 'functions',
    'messge': 'message',
    'messges': 'messages',
    'proccess': 'process',
    'sesion': 'session',
    'sesions': 'sessions',
    'validaton': 'validation',
    'validatons': 'validations',
}

# Unneeded words/phrases
UNNEEDED_WORDS = [
    'basically',
    'actually',
    'literally',
    'really',
    'very',
    'quite',
    'rather',
    'pretty',
    'just',
    'simply',
    'merely',
    'simply',
    'basically',
    'actually',
    'in order to',
    'due to the fact that',
    'as a matter of fact',
    'for all intents and purposes',
    'in the event that',
    'on the grounds that',
    'with regard to',
    'in respect of',
    'in connection with',
    'in accordance with',
    'in the first place',
    'at the end of the day',
    'when all is said and done',
    'at this point in time',
    'in this day and age',
    'for the most part',
    'in the final analysis',
    'in the long run',
    'in the short term',
    'in the meantime',
    'as far as I am concerned',
    'from my point of view',
    'in my opinion',
    'it seems to me',
    'I think that',
    'I believe that',
    'I feel that',
    'needless to say',
    'it goes without saying',
    'all things considered',
    'at any rate',
    'be that as it may',
    'by and large',
    'for what it is worth',
    'in any case',
    'in any event',
    'in other words',
    'on the other hand',
    'so to speak',
    'to all intents and purposes',
    'to make a long story short',
    'under the circumstances',
    'up to a point',
    'what with one thing and another',
]

def check_misspellings(content, filepath):
    """Check for misspellings"""
    issues = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments and strings for misspellings
        if line.strip().startswith('#'):
            continue
            
        for wrong, correct in COMMON_MISSPELLINGS.items():
            pattern = re.compile(rf'\b{re.escape(wrong)}\b', re.IGNORECASE)
            matches = pattern.finditer(line)
            for match in matches:
                issues.append({
                    'type': 'misspelling',
                    'file': filepath,
                    'line': line_num,
                    'column': match.start() + 1,
                    'found': match.group(),
                    'suggestion': correct,
                    'context': line.strip()
                })
    
    return issues

def check_unneeded_words(content, filepath):
    """Check for unneeded words"""
    issues = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue
            
        for phrase in UNNEEDED_WORDS:
            pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
            matches = pattern.finditer(line)
            for match in matches:
                issues.append({
                    'type': 'unneeded',
                    'file': filepath,
                    'line': line_num,
                    'column': match.start() + 1,
                    'found': match.group(),
                    'suggestion': 'remove',
                    'context': line.strip()
                })
    
    return issues

def check_code_blocks(content, filepath):
    """Check for problematic code blocks"""
    issues = []
    lines = content.split('\n')
    
    # Check for empty try/except blocks
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Empty try block
        if stripped == 'try:':
            if i + 1 < len(lines) and lines[i + 1].strip() in ['except:', 'except Exception:', 'except Exception as e:']:
                if i + 2 < len(lines) and lines[i + 2].strip() == 'pass':
                    issues.append({
                        'type': 'empty_block',
                        'file': filepath,
                        'line': i + 1,
                        'column': 1,
                        'found': 'empty try/except/pass block',
                        'suggestion': 'remove or implement',
                        'context': line.strip()
                    })
        
        # Long lines (over 120 characters)
        if len(line) > 120:
            issues.append({
                'type': 'long_line',
                'file': filepath,
                'line': i + 1,
                'column': 121,
                'found': f'line too long ({len(line)} chars)',
                'suggestion': 'break into multiple lines',
                'context': line.strip()[:80] + '...'
            })
        
        # Multiple consecutive empty lines
        if stripped == '':
            empty_count = 1
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                empty_count += 1
                j += 1
            if empty_count > 2:
                issues.append({
                    'type': 'empty_lines',
                    'file': filepath,
                    'line': i + 1,
                    'column': 1,
                    'found': f'{empty_count} consecutive empty lines',
                    'suggestion': 'reduce to max 2',
                    'context': 'multiple empty lines'
                })
    
    return issues

def check_comments(content, filepath):
    """Check for comment issues"""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # TODO comments without issue number
        if stripped.startswith('# TODO') and not re.search(r'# TODO\s*\(\d+\)', stripped):
            issues.append({
                'type': 'comment',
                'file': filepath,
                'line': i + 1,
                'column': 1,
                'found': 'TODO without issue number',
                'suggestion': 'add issue number',
                'context': stripped
            })
        
        # FIXME comments
        if stripped.startswith('# FIXME'):
            issues.append({
                'type': 'comment',
                'file': filepath,
                'line': i + 1,
                'column': 1,
                'found': 'FIXME comment',
                'suggestion': 'fix the issue',
                'context': stripped
            })
        
        # XXX comments
        if stripped.startswith('# XXX'):
            issues.append({
                'type': 'comment',
                'file': filepath,
                'line': i + 1,
                'column': 1,
                'found': 'XXX comment',
                'suggestion': 'address the hack',
                'context': stripped
            })
    
    return issues

def main():
    """Main search function"""
    print("COMPREHENSIVE SEARCH FOR MISSPELLINGS, UNNEEDED WORDS, AND CODE ISSUES")
    print("="*80)
    
    api_dir = "backend/app/api"
    all_issues = []
    files_checked = 0
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, api_dir)
                files_checked += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Run all checks
                    all_issues.extend(check_misspellings(content, rel_path))
                    all_issues.extend(check_unneeded_words(content, rel_path))
                    all_issues.extend(check_code_blocks(content, rel_path))
                    all_issues.extend(check_comments(content, rel_path))
                    
                except Exception as e:
                    all_issues.append({
                        'type': 'error',
                        'file': rel_path,
                        'line': 0,
                        'column': 0,
                        'found': f'Error reading file: {e}',
                        'suggestion': 'fix file',
                        'context': ''
                    })
    
    # Group issues by type
    by_type = defaultdict(list)
    for issue in all_issues:
        by_type[issue['type']].append(issue)
    
    # Print results
    print(f"\nFiles checked: {files_checked}")
    print(f"Total issues found: {len(all_issues)}")
    
    print(f"\nIssues by type:")
    for issue_type, issues in sorted(by_type.items()):
        print(f"  {issue_type}: {len(issues)}")
    
    # Show sample issues for each type
    print(f"\n{'='*80}")
    print("SAMPLE ISSUES BY TYPE")
    print(f"{'='*80}")
    
    for issue_type, issues in sorted(by_type.items()):
        if issues:
            print(f"\n{issue_type.upper()} ({len(issues)} total):")
            for issue in issues[:3]:
                print(f"  {issue['file']}:{issue['line']} - {issue['found']}")
                if issue['suggestion'] != 'remove':
                    print(f"    Suggestion: {issue['suggestion']}")
                if issue['context']:
                    print(f"    Context: {issue['context'][:80]}...")
    
    # Most common issues
    issue_counts = defaultdict(int)
    for issue in all_issues:
        if issue['type'] != 'error':
            issue_counts[issue['found']] += 1
    
    print(f"\n{'='*80}")
    print("TOP 10 MOST COMMON ISSUES")
    print(f"{'='*80}")
    
    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {issue}: {count} occurrences")
    
    print(f"\n{'='*80}")
    print("SEARCH COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
