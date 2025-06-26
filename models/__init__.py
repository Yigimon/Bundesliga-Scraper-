"""
Models package - Erweiterte Datenmodelle für Bundesliga Scraper
"""

from .extended_data import ExtendedMatchData, ExtendedGoal, Lineup, Player
from .game_data import GameData, Team, Goal

__all__ = [
    "ExtendedMatchData",
    "ExtendedGoal",
    "Lineup",
    "Player",
    "GameData",
    "Team",
    "Goal",
]
