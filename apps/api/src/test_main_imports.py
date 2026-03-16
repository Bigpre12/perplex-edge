import sys
import os

sys.path.append('.')

print("Testing database...", end=' ')
import db.session as database
print("✅ OK")

print("Testing services.cache...", end=' ')
from services.cache import cache
print("✅ OK")

print("Testing models.users...", end=' ')
import models.users
print("✅ OK")

print("Testing models.props...", end=' ')
import models.props
print("✅ OK")

print("Testing models.brain...", end=' ')
import models.brain
print("✅ OK")

print("Testing models.analytical...", end=' ')
import models.analytical
print("✅ OK")

print("Testing from models import HitRateModel...", end=' ')
try:
    from models import HitRateModel
    print("✅ OK")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("Testing direct from models.analytical import HitRateModel...", end=' ')
try:
    from models.analytical import HitRateModel
    print("✅ OK")
except Exception as e:
    print(f"❌ FAILED: {e}")
