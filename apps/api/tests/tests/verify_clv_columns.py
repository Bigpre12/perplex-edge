#!/usr/bin/env python3
"""
Verify CLV columns were added successfully
"""
import requests

def verify_clv_columns():
    """Verify CLV columns were added successfully"""
    
    print("VERIFYING CLV COLUMNS WERE ADDED")
    print("="*80)
    
    print("\nTo verify the columns were added, run this SQL:")
    print("SELECT column_name, data_type")
    print("FROM information_schema.columns")
    print("WHERE table_name = 'model_picks'")
    print("AND column_name IN (")
    print("    'closing_odds', 'clv_percentage', 'roi_percentage',")
    print("    'opening_odds', 'line_movement', 'sharp_money_indicator',")
    print("    'best_book_odds', 'best_book_name', 'ev_improvement'")
    print(")")
    print("ORDER BY column_name;")
    
    print("\nExpected output:")
    print("closing_odds | numeric")
    print("clv_percentage | numeric")
    print("roi_percentage | numeric")
    print("opening_odds | numeric")
    print("line_movement | numeric")
    print("sharp_money_indicator | numeric")
    print("best_book_odds | numeric")
    print("best_book_name | character varying")
    print("ev_improvement | numeric")
    
    print("\n" + "="*80)
    print("TROUBLESHOOTING:")
    print("="*80)
    
    print("\nIf columns weren't added:")
    print("1. Check for SQL errors when running ALTER TABLE")
    print("2. Verify you're connected to the correct database")
    print("3. Check permissions on the model_picks table")
    print("4. Try running commands individually")
    
    print("\nIf columns were added but picks still fail:")
    print("1. Backend might need to be restarted")
    print("2. Connection pool might be cached")
    print("3. Try waiting 1-2 minutes")
    
    print("\n" + "="*80)
    print("ALTERNATIVE APPROACH:")
    print("="*80)
    
    print("\nIf SQL commands don't work, try this:")
    print("1. Use Railway shell to access database")
    print("2. Or use pgAdmin/DBeaver to connect directly")
    print("3. Or use the SQL endpoint when available")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    
    print("\n1. Verify columns with the SQL query above")
    print("2. If missing, run ALTER TABLE commands again")
    print("3. If present, wait 2 minutes and test picks")
    print("4. Fix frontend BACKEND_URL")
    print("5. Test full system")

if __name__ == "__main__":
    verify_clv_columns()
