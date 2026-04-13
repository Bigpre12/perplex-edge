# apps/api/src/services/brains.py
import logging

from services.brain_sharp_money import SharpMoneyBrain
from services.brain_clv_tracker import BrainCLVTracker
from services.brain_injury_impact import InjuryImpactBrain
from services.brain_advanced_service import (
    BrainAdvancedService,
    brain_advanced_service,
)

logger = logging.getLogger(__name__)

sharp_money_brain = SharpMoneyBrain()
brain_clv_tracker = BrainCLVTracker()
injury_impact_brain = InjuryImpactBrain()
# brain_advanced_service imported singleton

logger.info("Brain singletons initialized in services/brains.py")
