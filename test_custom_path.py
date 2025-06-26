#!/usr/bin/env python3
"""
Test für den konfigurierbaren Download-Pfad
"""

import os
import asyncio
import sys
from pathlib import Path

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from scrapers.kicker_scraper import KickerScraper
from exporters.excel_exporter_new import ExcelExporter


async def test_custom_download_path():
    """Testet den benutzerdefinierten Download-Pfad."""
    print("🔍 Teste benutzerdefinierten Download-Pfad...")

    # Erstelle einen Test-Ordner
    custom_path = "downloads_test"
    os.makedirs(custom_path, exist_ok=True)
    print(f"📁 Test-Ordner erstellt: {os.path.abspath(custom_path)}")

    scraper = KickerScraper(rate_limit_delay=0.2)

    try:
        # Hole ein paar URLs zum Testen
        game_urls = await scraper.get_season_game_urls("2024-25")

        if game_urls and len(game_urls) >= 2:
            # Teste nur die ersten 2 Spiele
            test_urls = game_urls[:2]
            print(f"Teste {len(test_urls)} Spiele...")

            games = []
            for i, (url, matchday) in enumerate(test_urls):
                print(f"  {i+1}/2: Lade Spiel von Spieltag {matchday}...")
                try:
                    game = await scraper.parse_game_detail(url)
                    if game:
                        games.append(game)
                        print(f"    ✅ {game.home_team.name} vs {game.away_team.name}")
                    else:
                        print(f"    ❌ Spiel konnte nicht geparst werden")
                except Exception as e:
                    print(f"    ❌ Fehler: {e}")

            if games:
                print(f"\n✅ {len(games)} Spiele erfolgreich geladen")

                # Export in benutzerdefinierten Pfad
                exporter = ExcelExporter()
                exporter.set_output_directory(custom_path)
                exported_file = exporter.export_by_team(
                    games, f"test_custom_path_{len(games)}_spiele.xlsx"
                )

                print(f"📁 Export erfolgreich: {exported_file}")

                # Überprüfe, dass die Datei im richtigen Ordner ist
                if os.path.exists(exported_file) and custom_path in exported_file:
                    print(
                        "✅ Datei wurde im korrekten benutzerdefinierten Pfad gespeichert!"
                    )

                    # Zeige File-Größe
                    file_size = os.path.getsize(exported_file)
                    print(f"📊 Dateigröße: {file_size:,} Bytes")
                else:
                    print("❌ Datei wurde nicht im erwarteten Pfad gespeichert")

                # Aufräumen (optional)
                print(f"\n🗑️ Lösche Test-Ordner: {custom_path}")
                import shutil

                try:
                    shutil.rmtree(custom_path)
                    print("✅ Test-Ordner erfolgreich gelöscht")
                except:
                    print("⚠️ Test-Ordner konnte nicht gelöscht werden")

            else:
                print("❌ Keine Spiele erfolgreich geladen")
        else:
            print("❌ Nicht genügend URLs für Test verfügbar")

    except Exception as e:
        print(f"❌ Fehler: {e}")

    finally:
        await scraper.close()


async def main():
    """Hauptfunktion für Tests."""
    print("🚀 Starte Test für benutzerdefinierten Download-Pfad...\n")

    await test_custom_download_path()

    print("✅ Test abgeschlossen!")


if __name__ == "__main__":
    asyncio.run(main())
