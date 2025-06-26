"""
Erweiterte Datenklassen für Torschützen und Aufstellungen
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExtendedGoal:
    """Erweiterte Tor-Information mit Minutenangabe, Spieler und Team"""

    minute: str
    player: str
    team: str
    goal_type: str = "Standard"
    score_after: str = ""
    assist: Optional[str] = None


@dataclass
class Player:
    """Spieler-Information mit Namen, Bewertung und Team"""

    name: str
    team: str
    rating: Optional[str] = None
    position: Optional[str] = None


@dataclass
class Lineup:
    """Aufstellung eines Teams"""

    team: str
    players: List[Player]


@dataclass
class ExtendedMatchData:
    """Erweiterte Spiel-Daten mit Torschützen und Aufstellungen"""

    home_team: str
    away_team: str
    date: str
    home_score: int
    away_score: int
    goals: List[ExtendedGoal]
    lineups: List[Lineup]
    matchday: Optional[int] = None
    season: Optional[str] = None
