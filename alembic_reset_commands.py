#!/usr/bin/env python3
"""
Alembic reset commands for stuck migrations
"""
import requests

def alembic_reset_commands():
    """Alembic reset commands for stuck migrations"""
    
    print("ALEMBIC RESET COMMANDS FOR STUCK MIGRATIONS")
    print("="*80)
    
    print("\nCURRENT SITUATION:")
    print("- Railway deployment is in progress")
    print("- SQL endpoint not yet available")
    print("- Alembic migrations may be stuck")
    print("- CLV columns need to be added")
    
    print("\nDIRECT ALEMBIC COMMANDS:")
    print("If you have access to the Railway container shell, run these:")
    
    print("\n1. Check current migration version:")
    print("   alembic current")
    print("   SELECT * FROM alembic_version;")
    
    print("\n2. Check migration history:")
    print("   alembic history")
    
    print("\n3. Check if CLV columns exist:")
    print("   \\d model_picks")
    print("   \\c model_picks")
    print("   SELECT column_name FROM information_schema.columns WHERE table_name = 'model_picks' AND column_name IN ('closing_odds', 'clv_percentage', 'roi_percentage', 'opening_odds', 'line_movement', 'sharp_money_indicator', 'best_book_odds', 'best_book_name', 'ev_improvement') ORDER BY column_name;")
    
    print("\n4. Delete to reset (WARNING: This will lose migration history):")
    print("   DELETE FROM alembic_version;")
    
    print("\n5. After reset, run upgrade:")
    print("   alembic upgrade heads")
    
    print("\n6. Or stamp to a specific version:")
    print("   alembic stamp 20260207_010000")
    print("   alembic upgrade heads")
    
    print("\n7. Add CLV columns manually (if migration fails):")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS closing_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS clv_percentage NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS roi_percentage NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS opening_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS line_movement NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS sharp_money_indicator NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_odds NUMERIC(10, 4);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS best_book_name VARCHAR(50);")
    print("   ALTER TABLE model_picks ADD COLUMN IF NOT EXISTS ev_improvement NUMERIC(10, 4);")
    
    print("\n" + "="*80)
    print("OPTIONS:")
    print("1. Wait for SQL endpoint to deploy (recommended)")
    print("2. Use Railway container shell (if available)")
    print("3. Manual SQL commands (if you have direct DB access)")
    print("="*80)
    
    print("\nRECOMMENDED APPROACH:")
    print("1. Wait for Railway deployment to complete")
    print("2. Use SQL endpoint to add CLV columns")
    print("3. If still stuck, use Railway shell to run Alembic commands")
    print("4. Last resort: Manual SQL commands")
    
    print("\n" + "="*80)
    print("MIGRATION RESET: READY WHEN NEEDED")
    print("Commands provided for when SQL endpoint is available.")
    print("="*80)

if __name__ == "__main__":
    alembic_reset_commands()
