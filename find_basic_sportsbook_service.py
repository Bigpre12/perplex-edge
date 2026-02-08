#!/usr/bin/env python3
"""
Check if there's a basic sportsbook service
"""
import os

def find_basic_sportsbook_service():
    """Find basic sportsbook service"""
    services_dir = "c:\\Users\\preio\\perplex-edge\\backend\\app\\services"
    
    print("CHECKING FOR BASIC SPORTSBOOK SERVICE")
    print("="*80)
    
    # Look for any simple sportsbook service files
    for root, dirs, files in os.walk(services_dir):
        for file in files:
            if file.endswith('.py') and 'sportsbook' in file.lower():
                print(f"\nFound: {os.path.join(root, file)}")
                
                # Check if it has a simple class or function
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        if 'class' in content and 'SportsbookMonitor' in content:
                            print(f"   Contains SportsbookMonitor class")
                        elif 'def ' in content and 'sportsbook' in content:
                            print(f"   Contains sportsbook functions")
                except:
                    pass
    
    print("\n" + "="*80)

if __name__ == "__main__":
    find_basic_sportsbook_service()
