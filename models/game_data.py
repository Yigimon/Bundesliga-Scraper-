from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Player:
    """Repräsentiert einen Spieler."""

    name: str
    position: Optional[str] = None
    number: Optional[int] = None


@dataclass
class Goal:
    """Repräsentiert ein Tor."""

    scorer: str
    minute: int
    team: str
    assist: Optional[str] = None
    penalty: bool = False
    own_goal: bool = False


@dataclass
class Team:
    """Repräsentiert ein Team."""

    name: str
    players: List[Player] = field(default_factory=list)

    def add_player(self, player: Player):
        """Fügt einen Spieler zum Team hinzu."""
        self.players.append(player)


@dataclass
class GameData:
    """Repräsentiert ein Bundesliga-Spiel mit allen Details."""

    home_team: Team
    away_team: Team
    date: str
    home_score: int
    away_score: int
    season: str
    home_goals: List[Goal] = field(default_factory=list)
    away_goals: List[Goal] = field(default_factory=list)
    matchday: Optional[int] = None
    stadium: Optional[str] = None
    attendance: Optional[int] = None

    def get_total_goals(self) -> int:
        """Gibt die Gesamtanzahl der Tore zurück."""
        return self.home_score + self.away_score

    @property
    def teams(self) -> List[str]:
        """Gibt die Teamnamen als Liste zurück."""
        return [self.home_team.name, self.away_team.name]

    @property
    def score(self) -> tuple[int, int]:
        """Gibt das Ergebnis als Tupel zurück."""
        return (self.home_score, self.away_score)

    def get_winner(self) -> Optional[str]:
        """Gibt den Gewinner zurück oder None bei Unentschieden."""
        if self.home_score > self.away_score:
            return self.home_team.name
        elif self.away_score > self.home_score:
            return self.away_team.name
        return None

    def involves_team(self, team_name: str) -> bool:
        """Prüft ob ein Team an diesem Spiel beteiligt war."""
        return (
            self.home_team.name.lower() == team_name.lower()
            or self.away_team.name.lower() == team_name.lower()
        )

    def to_dict(self) -> dict:
        """Konvertiert das Spiel in ein Dictionary für Excel-Export."""
        return {
            "Datum": self.date,
            "Saison": self.season,
            "Spieltag": self.matchday or "",
            "Heimteam": self.home_team.name,
            "Auswärtsteam": self.away_team.name,
            "Ergebnis": f"{self.home_score}:{self.away_score}",
            "Tore_Heim": self.home_score,
            "Tore_Auswärts": self.away_score,
            "Tore_Gesamt": self.get_total_goals(),
            "Gewinner": self.get_winner() or "Unentschieden",
            "Torschützen_Heim": ", ".join([g.scorer for g in self.home_goals]),
            "Torschützen_Auswärts": ", ".join([g.scorer for g in self.away_goals]),
            "Stadion": self.stadium or "",
            "Zuschauer": self.attendance or "",
        }
