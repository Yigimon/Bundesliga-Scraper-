#!/usr/bin/env python3
"""
Direkter Test der verbesserten KickerScraper Integration
"""

import sys
import os
import asyncio
from pathlib import Path

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
current_dir = Path(__file__).parent
main_dir = current_dir.parent
sys.path.insert(0, str(main_dir))

from scrapers.kicker_scraper import KickerScraper
from bs4 import BeautifulSoup


async def test_verbesserte_extraktion():
    """Test der neuen Extraktion mit der lokalen HTML-Datei"""
    print("🚀 Test der verbesserten KickerScraper Integration\n")

    # Lade die lokale HTML-Datei
    html_file_path = (
        main_dir
        / "html"
        / "Spielschema ｜ Bor. Mönchengladbach - Bayer 04 Leverkusen 2：3 ｜ 1. Spieltag ｜ Bundesliga 2024_25 - kicker (24.6.2025 12：03：57).html"
    )

    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        scraper = KickerScraper()
        soup = BeautifulSoup(html_content, "html.parser")

        # Test Team-Namen
        home_team = "Bor. Mönchengladbach"
        away_team = "Bayer 04 Leverkusen"

        print("🔍 Teste Tor-Extraktion...")
        goals = scraper.extract_goals(soup, home_team, away_team)

        print(f"\n⚽ TORE-ERGEBNISSE:")
        print(f"   Anzahl Tore: {len(goals)}")
        for i, goal in enumerate(goals, 1):
            print(
                f"   {i}. {goal.get('minute', '?')}': {goal.get('player', 'Unbekannt')} ({goal.get('team', 'Unbekannt')}) - {goal.get('goal_type', 'N/A')}"
            )

        print("\n🔍 Teste Aufstellungen-Extraktion...")
        lineups = scraper.extract_lineups(soup, home_team, away_team)

        print(f"\n👥 AUFSTELLUNGEN-ERGEBNISSE:")
        print(f"   Anzahl Teams: {len(lineups)}")

        for lineup in lineups:
            team_name = lineup.get("team", "Unbekannt")
            players = lineup.get("players", [])
            print(f"   {team_name}: {len(players)} Spieler")
            if players:
                print(f"     Erste 5: {', '.join(players[:5])}")

        # Bewertung
        print(f"\n📊 BEWERTUNG:")
        print(f"   ✅ Tore extrahiert: {'JA' if goals else 'NEIN'} ({len(goals)} Tore)")
        print(
            f"   ✅ Aufstellungen extrahiert: {'JA' if lineups else 'NEIN'} ({sum(len(l.get('players', [])) for l in lineups)} Spieler total)"
        )

        if goals and lineups:
            print("\n🎉 Integration erfolgreich! Moderne Parser funktionieren.")
        else:
            print("\n⚠️ Integration unvollständig. Debugging erforderlich.")

        # Details für Debugging
        if not goals:
            print("\n🔍 Debugging - Tore-Sektion:")
            h4_elements = soup.find_all("h4")
            for h4 in h4_elements:
                text = h4.get_text().strip()
                if "Tore" in text or "tore" in text.lower():
                    print(f"     Gefunden: '{text}' - Klasse: {h4.get('class', [])}")

        if not lineups:
            print("\n🔍 Debugging - Aufstellungs-Sektion:")
            sections = soup.find_all("section")
            for section in sections:
                section_class = section.get("class", [])
                print(f"     Section gefunden - Klasse: {section_class}")
                headers = section.find_all(["h4", "h3", "h2"])
                for header in headers:
                    text = header.get_text().strip()
                    if "Aufstellung" in text or "aufstellung" in text.lower():
                        print(f"       Header: '{text}'")

    except FileNotFoundError:
        print(f"❌ HTML-Datei nicht gefunden: {html_file_path}")
        return
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_verbesserte_extraktion())
