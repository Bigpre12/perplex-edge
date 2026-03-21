from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic/MetaData discovery
from models.user import User, PushSubscription, APIKey, UserOverride
from models.saved_system import SavedSystem
from models.line_move import LineMove
from models.brain import (
    BrainSystemState, ModelPick, SharpSignal, BrainLog, SteamSnapshot,
    WhaleMove, CLVRecord, SteamEvent, HitRateModel, PlayerStats, InjuryImpactEvent, 
    NeuralEdge, RefereeGame, Schedule, Signal, InjuryImpact, LinePrediction, 
    UnifiedOdds, UnifiedEVSignal, LineTick, UnifiedEVSignalHistory, PropLive, 
    PropHistory, EdgeEVHistory
)
from models.injury import Injury
from models.prop import Prop, PropLine, PropOdds, GameLine, GameLineOdds, LiveGameStat, Market, Sport
from models.bet import Bet, BetSlip, BetLeg, BetLog, BetResult
from models.heartbeat import Heartbeat
from models.contests import Contest, ContestEntry, ContestPick
from models.snapshots import DatabaseSnapshot

