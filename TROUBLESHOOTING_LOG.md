# Troubleshooting Log - Feb 7, 2026 10:10 PM CT

## Current Issues

### 1. Grading Endpoint 404
- URL: `https://railway-engine-production.up.railway.app/api/grading/health`
- Returns: `{"detail":"Not Found"}` (404)
- Root endpoint works: `{"message":"Perplex Edge API","version":"0.1.0","status":"running"}` (200)
- Health endpoint works: `/api/health` returns 200

### 2. Likely Cause: scipy Import Failure
- Local test: `from app.api.grading import router` fails with `ModuleNotFoundError: No module named 'scipy'`
- scipy was added to requirements.txt but may not be installed on Railway yet
- Grading router import chain: grading → pick_grader → model → probability_calibration → scipy

### 3. Frontend 502 Errors
- `https://perplex-edge-production.up.railway.app/api/grading/health` returns 502 Bad Gateway
- nginx config has `proxy_ssl_verify off` and points to `https://railway-engine-production.up.railway.app/api/`
- Backend appears to be running (responds to root and /api/health)

### 4. Backend Model Generation Working
- Database queries executing successfully
- Model generating picks based on player statistics
- SQLAlchemy logs showing active queries to player_game_stats table

## What Needs to be Fixed

1. **Verify scipy is installed on Railway backend**
   - Check deploy logs for "Successfully installed scipy"
   - If not installed, may need to trigger rebuild or check requirements.txt

2. **Verify grading router loads without errors**
   - Check Railway deploy logs for import errors during startup
   - Look for: `ImportError`, `ModuleNotFoundError`, `Failed to start application`

3. **Fix frontend nginx backend URL**
   - Currently hardcoded to `https://railway-engine-production.up.railway.app/api/`
   - Should this use Railway internal URL instead?
   - Or is the public URL correct but backend not fully responding?

4. **Test grading endpoints once router loads**
   - `/api/grading/health` should return `{"status": "ok", "router": "grading"}`
   - `/api/grading/debug/picks-status` should show pick counts
   - `/api/grading/admin/activate-test-picks` should activate hidden picks

## Questions for Decision

1. **Should we use Railway internal networking (http://service.railway.internal:8080) instead of public HTTPS URLs?**
   - This would avoid SSL handshake issues
   - Faster, more secure
   - Requires knowing the exact backend service name

2. **Is scipy actually installed on the Railway backend?**
   - Check deploy logs for confirmation
   - May need to trigger a clean rebuild if package installation failed

3. **Should we simplify the grading router to remove the scipy dependency temporarily?**
   - This would let us test the API endpoints immediately
   - Can add scipy functionality back later

4. **What's the exact Railway backend service name for internal networking?**
   - Need to check Railway dashboard
   - Format would be: `http://[service-name].railway.internal:8080`

## Next Steps Needed

1. Check Railway backend deploy logs for scipy installation status
2. Determine if we should use internal Railway URLs or public URLs
3. Verify grading router imports successfully
4. Test all grading endpoints
5. Activate test picks once endpoints work
6. Verify frontend can connect to backend

## How to Fix?

Options:
A. Fix scipy installation and verify router loads
B. Use Railway internal networking for frontend→backend
C. Simplify grading router to remove scipy dependency
D. Combination of A + B

Which approach should we take?
