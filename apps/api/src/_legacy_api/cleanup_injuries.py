
import sys
import os

file_path = r'c:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src\api\immediate_working.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We know the range for /injuries junk and /injuries/active is approximately 1627 to 1929
# However, let's find the exact indices by looking for key strings
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if '# Removing legacy injuries block' in line and start_idx == -1:
        start_idx = i
    if '@router.get("/injuries/out")' in line and end_idx == -1:
        end_idx = i

if start_idx != -1 and end_idx != -1:
    print(f"Cleaning from {start_idx} to {end_idx}")
    new_code = [
        '\n',
        '@router.get("/injuries/active")\n',
        'async def get_active_injuries(\n',
        '    sport: str = Query("basketball_nba", description="The Odds API sport key"),\n',
        '    limit: int = Query(20, description="Number of active injuries to return")\n',
        '):\n',
        '    """Get active injuries (High/Medium impact)"""\n',
        '    try:\n',
        '        from services.injury_service import fetch_injuries\n',
        '        sport_short = sport.split("_")[-1] if "_" in sport else sport\n',
        '        injuries = await fetch_injuries(sport_short)\n',
        '        active_injuries = [i for i in injuries if i["impact"] in ["high", "medium"]]\n',
        '        return {\n',
        '            "active_injuries": active_injuries[:limit],\n',
        '            "total": len(active_injuries),\n',
        '            "status": "live",\n',
        '            "timestamp": datetime.now(timezone.utc).isoformat()\n',
        '        }\n',
        '    except Exception as e:\n',
        '        return {"error": str(e), "active_injuries": [], "timestamp": datetime.now(timezone.utc).isoformat()}\n',
        '\n'
    ]
    lines[start_idx:end_idx] = new_code
    
    # Also fix the /injuries/out endpoint which starts right after our new code
    # Actually, let's just replace everything from start_idx to the end of the /injuries/out function
    # Let's find where the next function or the end of /injuries/out is
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully cleaned the file.")
else:
    print(f"Could not find indices: start={start_idx}, end={end_idx}")
