from database import Base

from .props import PropLine, PropOdds, LiveGameStat
from .bets import BetLog, BetSlip
from .users import User, PushSubscription, APIKey
from .social import PublicSlate, OddsAlert
from .contests import Contest, ContestEntry
from .kalshi import KalshiMarket

# For legacy dummy models not yet migrated
from sqlalchemy import Column, Integer
class DummyModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)

class Referral(DummyModel): __tablename__ = 'referral'
class PlayerStats(DummyModel): __tablename__ = 'playerstats'
class RefereeGame(DummyModel): __tablename__ = 'refereegame'
class Schedule(DummyModel): __tablename__ = 'schedule'
