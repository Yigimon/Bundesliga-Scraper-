#!/usr/bin/env python3
"""
Test-Skript um zu verifizieren, dass der Export-Fix funktioniert.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from exporters.excel_exporter_new import ExcelExporter
from models.game_data import GameData, Team


def create_test_game():
    """Erstelle ein Test-Spiel für den Export-Test"""
    home_team = Team(name="Bayern München")
    away_team = Team(name="Borussia Dortmund")

    game = GameData(
        home_team=home_team,
        away_team=away_team,
        date="2024-12-01",
        season="2024-25",
        home_score=2,
        away_score=1,
        home_goals=[],
        away_goals=[],
        matchday=10,
    )
    return game


def test_export_path():
    """Teste ob der Export in den korrekten Pfad erfolgt"""
    print("🧪 Teste Export-Pfad Fix...")

    # Test-Spiel erstellen
    games = [create_test_game()]

    # ExcelExporter instanziieren
    exporter = ExcelExporter()

    # Nur Dateiname übergeben (wie im Fix)
    filename = "test_export_fix.xlsx"

    try:
        export_path = exporter.export_by_team(games, filename)
        print(f"✅ Export erfolgreich: {export_path}")

        # Prüfe ob Datei im korrekten Pfad erstellt wurde
        expected_path = Path("exports") / filename
        if expected_path.exists():
            print(f"✅ Datei existiert im korrekten Pfad: {expected_path.absolute()}")

            # Prüfe dass KEINE doppelte exports/exports Struktur erstellt wurde
            wrong_path = Path("exports") / "exports" / filename
            if wrong_path.exists():
                print(
                    f"❌ FEHLER: Datei wurde auch im falschen Pfad erstellt: {wrong_path}"
                )
            else:
                print("✅ Keine doppelte exports/exports Struktur erstellt")

            # Cleanup
            expected_path.unlink()
            print("🧹 Test-Datei gelöscht")

        else:
            print(
                f"❌ FEHLER: Datei nicht im erwarteten Pfad gefunden: {expected_path}"
            )

    except Exception as e:
        print(f"❌ FEHLER beim Export: {e}")


if __name__ == "__main__":
    test_export_path()
    print("🏁 Test abgeschlossen")
