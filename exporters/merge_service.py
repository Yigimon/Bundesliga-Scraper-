"""
# MergeService - Vereinfachte Implementierung für das aufgeräumte Projekt
# Verschiebt Merge-Funktionalität in den Exporters-Ordner
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MergeService:
    """Service zum Zusammenführen von neuen Spieldaten mit existierenden Excel-Dateien."""

    def __init__(self):
        """Initialisiert den MergeService."""
        self.logger = logger

    def merge_with_existing(
        self, new_data: List[Dict[str, Any]], excel_path: str
    ) -> bool:
        """
        Fügt neue Spieldaten zu einer existierenden Excel-Datei hinzu.

        Args:
            new_data: Liste der neuen Spieldaten
            excel_path: Pfad zur existierenden Excel-Datei

        Returns:
            bool: True wenn erfolgreich, False bei Fehlern
        """
        try:
            excel_file = Path(excel_path)

            if not excel_file.exists():
                self.logger.info(f"Excel-Datei existiert nicht: {excel_path}")
                return False

            # Neue Daten in DataFrame konvertieren
            new_df = pd.DataFrame(new_data)

            if new_df.empty:
                self.logger.info("Keine neuen Daten zum Zusammenführen")
                return True

            # Existierende Daten laden
            with pd.ExcelFile(excel_path) as existing_file:
                sheet_names = existing_file.sheet_names

                # Für jedes Sheet prüfen und zusammenführen
                with pd.ExcelWriter(
                    excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
                ) as writer:
                    for sheet_name in sheet_names:
                        existing_df = pd.read_excel(excel_path, sheet_name=sheet_name)

                        # Neue Daten filtern, die zu diesem Sheet gehören
                        # (vereinfachte Logik - in der Praxis würde man nach Verein filtern)
                        combined_df = pd.concat(
                            [existing_df, new_df], ignore_index=True
                        )

                        # Duplikate entfernen (basierend auf Datum, Heimteam, Auswärtsteam)
                        if all(
                            col in combined_df.columns
                            for col in ["Datum", "Heimteam", "Auswärtsteam"]
                        ):
                            combined_df = combined_df.drop_duplicates(
                                subset=["Datum", "Heimteam", "Auswärtsteam"],
                                keep="last",
                            )

                        # Zurück in Excel schreiben
                        combined_df.to_excel(writer, sheet_name=sheet_name, index=False)

            self.logger.info(
                f"Erfolgreich {len(new_data)} neue Datensätze zusammengeführt"
            )
            return True

        except Exception as e:
            self.logger.error(f"Fehler beim Zusammenführen: {e}")
            return False

    def backup_existing_file(self, excel_path: str) -> str:
        """
        Erstellt ein Backup der existierenden Excel-Datei.

        Args:
            excel_path: Pfad zur Excel-Datei

        Returns:
            str: Pfad zum Backup oder None bei Fehlern
        """
        try:
            excel_file = Path(excel_path)
            if not excel_file.exists():
                return None

            backup_path = excel_file.with_suffix(f".backup{excel_file.suffix}")
            excel_file.rename(backup_path)

            self.logger.info(f"Backup erstellt: {backup_path}")
            return str(backup_path)

        except Exception as e:
            self.logger.error(f"Fehler beim Backup erstellen: {e}")
            return None

    def merge_gamedata_with_existing(self, games, excel_path: str):
        """
        Fügt GameData-Objekte zu einer existierenden Excel-Datei hinzu.

        Args:
            games: Liste der GameData-Objekte
            excel_path: Pfad zur existierenden Excel-Datei

        Returns:
            bool: True wenn erfolgreich, False bei Fehlern
        """
        # Konvertiere GameData-Objekte zu Dictionaries
        if hasattr(games, "__iter__"):
            game_dicts = []
            for game in games:
                if hasattr(game, "to_dict"):
                    game_dicts.append(game.to_dict())
                else:
                    # Fallback für Objekte ohne to_dict
                    game_dict = {
                        "Datum": getattr(game, "date", ""),
                        "Heimteam": (
                            getattr(game, "home_team", {}).get("name", "")
                            if hasattr(getattr(game, "home_team", {}), "get")
                            else str(getattr(game, "home_team", ""))
                        ),
                        "Auswärtsteam": (
                            getattr(game, "away_team", {}).get("name", "")
                            if hasattr(getattr(game, "away_team", {}), "get")
                            else str(getattr(game, "away_team", ""))
                        ),
                        "Ergebnis": f"{getattr(game, 'home_score', 0)}:{getattr(game, 'away_score', 0)}",
                    }
                    game_dicts.append(game_dict)

            return self.merge_with_existing(game_dicts, excel_path)
        else:
            return games  # Rückgabe der ursprünglichen games falls kein Merge möglich
