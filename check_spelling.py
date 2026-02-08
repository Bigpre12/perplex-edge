#!/usr/bin/env python3
"""
Check for misspellings and unneeded words in API files
Run 10 iterations to catch all issues
"""
import os
import re
import random
from collections import defaultdict

# Common misspellings to check
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
    'responce': 'responses',
    'requst': 'request',
    'requsts': 'requests',
    'authenication': 'authentication',
    'authorzation': 'authorization',
    'conection': 'connection',
    'conection': 'connections',
    'databse': 'database',
    'databses': 'databases',
    'excecute': 'execute',
    'excecution': 'execution',
    'funtion': 'function',
    'funtions': 'functions',
    'messge': 'message',
    'messges': 'messages',
    'proccess': 'process',
    'proccessing': 'processing',
    'proccessor': 'processor',
    'sesion': 'session',
    'sesions': 'sessions',
    'validaton': 'validation',
    'validaton': 'validations',
}

# Unneeded words/phrases to check
UNNEEDED_PHRASES = [
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
]

def check_file(filepath, iteration):
    """Check a single file for issues"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for misspellings
        for wrong, correct in COMMON_MISSPELLINGS.items():
            pattern = re.compile(rf'\b{re.escape(wrong)}\b', re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    issues.append({
                        'type': 'misspelling',
                        'line': line_num,
                        'column': match.start() + 1,
                        'found': match.group(),
                        'suggestion': correct,
                        'context': line.strip()
                    })
        
        # Check for unneeded words/phrases
        for phrase in UNNEEDED_PHRASES:
            pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    issues.append({
                        'type': 'unneeded',
                        'line': line_num,
                        'column': match.start() + 1,
                        'found': match.group(),
                        'suggestion': 'remove',
                        'context': line.strip()
                    })
        
        # Check for double spaces
        for line_num, line in enumerate(lines, 1):
            if '  ' in line:
                issues.append({
                    'type': 'formatting',
                    'line': line_num,
                    'column': line.find('  ') + 1,
                    'found': 'double space',
                    'suggestion': 'single space',
                    'context': line.strip()
                })
        
        # Check for trailing whitespace
        for line_num, line in enumerate(lines, 1):
            if line.endswith(' '):
                issues.append({
                    'type': 'formatting',
                    'line': line_num,
                    'column': len(line.rstrip()) + 1,
                    'found': 'trailing space',
                    'suggestion': 'remove',
                    'context': repr(line)
                })
        
        # Check for inconsistent quotes (single vs double)
        single_quotes = len(re.findall(r"'[^']'", content))
        double_quotes = len(re.findall(r'"[^"]"', content))
        if single_quotes > 0 and double_quotes > 0:
            issues.append({
                'type': 'consistency',
                'line': 0,
                'column': 0,
                'found': f'mixed quotes: {single_quotes} single, {double_quotes} double',
                'suggestion': 'use consistent quotes',
                'context': 'file level'
            })
        
    except Exception as e:
        issues.append({
            'type': 'error',
            'line': 0,
            'column': 0,
            'found': f'Error reading file: {e}',
            'suggestion': 'fix file encoding',
            'context': filepath
        })
    
    return issues

def run_check(iteration):
    """Run one iteration of the check"""
    api_dir = "backend/app/api"
    all_issues = []
    files_checked = 0
    
    print(f"\n{'='*80}")
    print(f"ITERATION {iteration}/10")
    print(f"{'='*80}")
    
    # Randomize file order for each iteration
    all_files = []
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                all_files.append(os.path.join(root, filename))
    
    random.shuffle(all_files)
    
    for filepath in all_files:
        issues = check_file(filepath, iteration)
        if issues:
            all_issues.extend(issues)
            print(f"\n{os.path.relpath(filepath, api_dir)}:")
            for issue in issues[:5]:  # Show max 5 issues per file
                print(f"  Line {issue['line']}: {issue['type'].upper()} - {issue['found']}")
                if issue['suggestion'] != 'remove':
                    print(f"    Suggestion: {issue['suggestion']}")
                print(f"    Context: {issue['context'][:80]}...")
        files_checked += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"ITERATION {iteration} SUMMARY:")
    print(f"  Files checked: {files_checked}")
    print(f"  Total issues found: {len(all_issues)}")
    
    # Group by type
    by_type = defaultdict(int)
    for issue in all_issues:
        by_type[issue['type']] += 1
    
    print(f"  Issues by type:")
    for issue_type, count in sorted(by_type.items()):
        print(f"    {issue_type}: {count}")
    
    return all_issues

def main():
    """Run 10 iterations of the check"""
    print("RUNNING 10 ITERATIONS OF SPELLING AND WORD CHECKS")
    print("="*80)
    
    all_iterations_issues = []
    
    for i in range(1, 11):
        issues = run_check(i)
        all_iterations_issues.append(issues)
        
        # Brief pause between iterations
        if i < 10:
            print(f"\nWaiting 1 second before next iteration...")
            import time
            time.sleep(1)
    
    # Final summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY - ALL 10 ITERATIONS")
    print(f"{'='*80}")
    
    # Find unique issues across all iterations
    unique_issues = set()
    for issues in all_iterations_issues:
        for issue in issues:
            # Create a unique key for the issue
            key = (issue['type'], issue['found'], issue.get('context', '')[:50])
            unique_issues.add(key)
    
    print(f"Total unique issues found: {len(unique_issues)}")
    
    # Most common issues
    issue_counts = defaultdict(int)
    for issues in all_iterations_issues:
        for issue in issues:
            issue_counts[issue['found']] += 1
    
    print(f"\nTop 10 most common issues:")
    for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {issue}: {count} occurrences")
    
    print(f"\n{'='*80}")
    print("CHECK COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
