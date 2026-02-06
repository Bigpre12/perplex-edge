# Database Scripts

This directory contains scripts for database maintenance and data fixes.

## Sport Mapping Fix Scripts

### Problem
NBA players (Austin Reaves, Derrick White, Rui Hachimura, Jayson Tatum) were incorrectly assigned NHL sport_id (53) instead of NBA sport_id (30).

### Scripts Available

#### 1. fix_all_sport_mappings.py (Recommended)
**Comprehensive fix for all sport mapping issues**
- Checks ALL players for sport_id mismatches
- Fixes players based on their team's actual sport
- Updates all related tables (model_picks, player_hit_rates, etc.)
- Provides detailed reporting

#### 2. fix_sport_mapping.py
**Targeted fix for NBA players with NHL sport_id**
- Specifically fixes NBA players incorrectly assigned to NHL
- Updates all related records

#### 3. fix_nhl_player_sport_ids.py
**Ensures NHL players have correct sport_id**
- Fixes NHL players that might have wrong sport_id
- Complementary to NBA fix

## Usage

### Quick Fix (Recommended)
```bash
cd backend
python scripts/fix_all_sport_mappings.py
```

### Targeted Fixes
```bash
# Fix NBA players only
python scripts/fix_sport_mapping.py

# Fix NHL players only  
python scripts/fix_nhl_player_sport_ids.py
```

## What These Scripts Do

1. **Identify Issues**: Find players with wrong sport_id based on their team's sport
2. **Update Records**: Fix sport_id in all related tables:
   - players
   - model_picks
   - player_hit_rates
   - player_market_hit_rates
   - injuries
3. **Verify Fixes**: Confirm no mismatches remain
4. **Report Results**: Show what was fixed and player counts by sport

## Sport ID Mappings

- **NBA**: 30
- **NHL**: 53
- **NFL**: 31
- **NCAAB**: 32
- **NCAAF**: 41
- **MLB**: 40
- **WNBA**: 34
- **ATP**: 42
- **WTA**: 43
- **PGA**: 60
- **EPL**: 70
- **UCL**: 71
- **MLS**: 72
- **UEL**: 73
- **UECL**: 74
- **UFC**: 80

## Running in Production

1. **Backup Database**: Always backup before running fixes
2. **Test in Staging**: Run scripts in staging first
3. **Monitor Logs**: Watch for any errors during execution
4. **Verify Results**: Check that fixes worked as expected

## After Running Fixes

1. **Restart Services**: Restart backend services to clear any cached data
2. **Verify Frontend**: Check that player props show correct sports
3. **Monitor Brain Service**: Ensure brain service detects the fixes
4. **Check API Endpoints**: Verify sport filtering works correctly

## Safety Features

- **Dry Run Mode**: Scripts report what they'll fix before making changes
- **Rollback Ready**: Changes can be reverted if needed
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **Verification Step**: Confirms fixes worked correctly
