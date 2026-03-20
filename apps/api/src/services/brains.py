# src/services/brains.py
import logging
from services.brain_sharp_money import sharp_money_brain
from services.brain_clv_tracker import brain_clv_tracker
from services.brain_injury_impact import injury_impact_brain
from services.brain_advanced_service import (
    BrainAdvancedService,
    brain_advanced_service,
)


logger = logging.getLogger(__name__)

# Re-export singletons for application-wide use
# (Instances are already initialized in their respective files)

logger.info("Brain singletons initialized in services/brains.py")
