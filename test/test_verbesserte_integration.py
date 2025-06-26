"""
Test der verbesserten KickerScraper Integration
"""

import asyncio
from scrapers.kicker_scraper import KickerScraper
from bs4 import BeautifulSoup


async def test_verbesserte_extraktion():
    """Test der neuen Extraktion mit der lokalen HTML-Datei"""
    print("🚀 Test der verbesserten KickerScraper Integration\n")

    # Lade die lokale HTML-Datei
    html_file_path = r"c:\Users\yigit\OneDrive\Desktop\CODING\Backup Kicker.de\kicker v2.3 muster\html\Spielschema ｜ Bor. Mönchengladbach - Bayer 04 Leverkusen 2：3 ｜ 1. Spieltag ｜ Bundesliga 2024_25 - kicker (24.6.2025 12：03：57).html"

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
                print(
                    f"     Beispiele: {', '.join(players[:5])}{'...' if len(players) > 5 else ''}"
                )

        # Bewertung
        print(f"\n📊 BEWERTUNG:")
        print(f"   ✅ Tore extrahiert: {'JA' if goals else 'NEIN'} ({len(goals)} Tore)")
        print(
            f"   ✅ Aufstellungen extrahiert: {'JA' if lineups else 'NEIN'} ({len(lineups)} Teams)"
        )

        if goals and lineups:
            home_lineup = next((l for l in lineups if l["team"] == home_team), None)
            away_lineup = next((l for l in lineups if l["team"] == away_team), None)

            home_count = len(home_lineup["players"]) if home_lineup else 0
            away_count = len(away_lineup["players"]) if away_lineup else 0

            print(f"   📈 Qualität:")
            print(f"     Tore: {len(goals)}/5 erwartet")
            print(f"     Aufstellung Heim: {home_count}/11 Spieler")
            print(f"     Aufstellung Auswärts: {away_count}/11 Spieler")

            success_rate = (
                (len(goals) / 5 * 100)
                + (home_count / 11 * 100)
                + (away_count / 11 * 100)
            ) / 3

            print(f"   🎯 Gesamt-Erfolgsrate: {success_rate:.1f}%")

    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_verbesserte_extraktion())
