"""
Kicker.de HTML Structure Analyzer and Parser
============================================

Analysiert moderne kicker.de Spielschema-Seiten und extrahiert:
- Torschützen mit Zeit und Art des Tors
- Startaufstellungen beider Teams
- Einwechslungen und Auswechslungen

Optimiert für die HTML-Struktur von 2024/25 mit Fallback-Strategien.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple, Union
from bs4 import BeautifulSoup, Tag
import httpx


class ModernKickerParser:
    """
    Parser für moderne kicker.de HTML-Strukturen (2024/25+)
    mit robusten Fallback-Strategien für ältere Strukturen
    """

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

    async def fetch_schema_page(self, url: str) -> Optional[str]:
        """Lädt eine kicker.de Schema-Seite"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Fehler beim Laden von {url}: {e}")
            return None

    def extract_goals_modern(
        self, soup: BeautifulSoup
    ) -> List[Dict[str, Union[str, int]]]:
        """
        Extrahiert Torschützen aus moderner HTML-Struktur (2024/25)

        Die Tore-Struktur ist:
        <h4>Tore</h4>
        <div class="kick__goals-presorted">
            <div class="kick__goals kick__goals--ingame">
                <div class="kick__goals__row">
                    <!-- Tor-Daten hier -->
                </div>
            </div>
        </div>

        Returns:
            Liste mit Tor-Dictionaries: [{"minute": int, "scorer": str, "team": str, "type": str}]
        """
        goals = []

        # Suche nach dem Tore-Header (h4 mit Text "Tore")
        h4_elements = soup.find_all("h4", class_="kick__card-headline")
        tore_h4 = None

        for h4 in h4_elements:
            if h4.get_text().strip() == "Tore":
                tore_h4 = h4
                break

        if not tore_h4:
            print("⚠️ Keine Tore-Sektion gefunden")
            return goals

        # Finde den Container nach dem h4
        tore_container = tore_h4.find_next_sibling()
        while tore_container and tore_container.name != "div":
            tore_container = tore_container.find_next_sibling()

        if not tore_container:
            print("⚠️ Kein Tore-Container gefunden")
            return goals

        # Suche nach allen kick__goals__row Elementen
        goal_rows = tore_container.find_all("div", class_="kick__goals__row")
        print(f"🔍 Gefundene Tor-Rows: {len(goal_rows)}")

        for row in goal_rows:
            goal_data = self._parse_goal_row_modern(row)
            if goal_data:
                goals.append(goal_data)

        return goals

    def _parse_goal_row_modern(self, row: Tag) -> Optional[Dict[str, Union[str, int]]]:
        """
        Parst eine einzelne kick__goals__row aus der modernen Struktur

        Struktur:
        <div class="kick__goals__row">
            <div class="kick__goals__team kick__goals__team--left">
                <a class="kick__goals__player" href="...">
                    <span class="kick__substitutions--hide-mobile">Spielername</span>
                </a>
                <div class="kick__assist__player"><span>Tor-Art</span></div>
            </div>
            <span class="kick__goals__time kick__goals__time--left">59'</span>
            <div class="kick__goals__score">...</div>
            <span class="kick__goals__time">38'</span>
            <div class="kick__goals__team kick__goals__team--right">...</div>
        </div>
        """
        try:
            # Suche nach Spieler-Link (links oder rechts)
            player_links = row.find_all("a", class_="kick__goals__player")

            for player_link in player_links:
                # Bestimme Team-Seite
                team_container = player_link.find_parent(
                    "div", class_="kick__goals__team"
                )
                if not team_container:
                    continue

                team_classes = team_container.get("class", [])
                if "kick__goals__team--left" in team_classes:
                    team_side = "home"
                    # Zeit aus dem --left Element
                    time_elem = row.find("span", class_="kick__goals__time--left")
                elif "kick__goals__team--right" in team_classes:
                    team_side = "away"
                    # Zeit aus dem regulären Element (ohne --left)
                    time_elems = row.find_all("span", class_="kick__goals__time")
                    time_elem = None
                    for elem in time_elems:
                        if "kick__goals__time--left" not in elem.get("class", []):
                            time_elem = elem
                            break
                else:
                    continue

                # Spielername extrahieren
                name_span = player_link.find(
                    "span", class_="kick__substitutions--hide-mobile"
                )
                if name_span:
                    scorer_name = name_span.get_text().strip()
                else:
                    scorer_name = player_link.get_text().strip()

                if not scorer_name:
                    continue

                # Zeit extrahieren
                minute = 0
                if time_elem:
                    time_text = time_elem.get_text().strip()
                    minute = self._parse_time_to_minutes(time_text)

                # Tor-Art extrahieren
                goal_type = ""
                assist_elem = team_container.find("div", class_="kick__assist__player")
                if assist_elem:
                    type_span = assist_elem.find("span")
                    if type_span:
                        goal_type = type_span.get_text().strip()

                return {
                    "minute": minute,
                    "scorer": scorer_name,
                    "team": team_side,
                    "type": goal_type,
                }

        except Exception as e:
            print(f"⚠️ Fehler beim Parsen einer Goal-Row: {e}")

        return None

    def extract_lineups_modern(
        self, soup: BeautifulSoup
    ) -> Tuple[List[str], List[str]]:
        """
        Extrahiert Startaufstellungen aus moderner HTML-Struktur

        Returns:
            Tuple (home_team_players, away_team_players)
        """
        home_players = []
        away_players = []

        # Suche nach der Aufstellungs-Sektion
        sections = soup.find_all("section", class_="kick__section-item")
        for section in sections:
            header = section.find("header")
            if header and header.find("h4"):
                h4_text = header.find("h4").get_text().strip()
                if "Aufstellung" in h4_text:
                    # Linkes Team (Heimteam)
                    left_team = section.find("div", class_="kick__lineup__team--left")
                    if left_team:
                        home_players = self._extract_team_players(left_team)

                    # Rechtes Team (Auswärtsteam)
                    right_team = section.find("div", class_="kick__lineup__team--right")
                    if right_team:
                        away_players = self._extract_team_players(right_team)
                    break

        return home_players, away_players

    def _extract_team_players(self, team_container: Tag) -> List[str]:
        """Extrahiert Spielernamen aus einem Team-Container"""
        players = []

        # Suche nach der ungeordneten Liste mit Spielern
        lineup_list = team_container.find(
            "div", class_="kick__lineup-text__unorderedList"
        )
        if lineup_list:
            # Alle div-Elemente mit Spieler-Links
            player_divs = lineup_list.find_all("div")

            for div in player_divs:
                # Spieler-Link suchen
                player_link = div.find("a", href=re.compile(r"/spieler/"))
                if player_link:
                    player_name = player_link.get_text().strip()
                    # Bereinige den Namen (entferne Bewertungen etc.)
                    player_name = self._clean_player_name(player_name)
                    if player_name:
                        players.append(player_name)

        return players

    def _clean_player_name(self, raw_name: str) -> str:
        """Bereinigt Spielernamen von Zusatzinformationen"""
        # Entferne häufige Zusätze wie Bewertungen, Symbole etc.
        clean_name = re.sub(r"\d+[.,]\d+", "", raw_name)  # Bewertungen wie "2,5"
        clean_name = re.sub(r"[0-9]+", "", clean_name)  # Zahlen
        clean_name = re.sub(r"\s+", " ", clean_name)  # Mehrfache Leerzeichen
        return clean_name.strip()

    def extract_substitutions_modern(
        self, soup: BeautifulSoup
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Extrahiert Wechsel aus moderner HTML-Struktur

        Returns:
            Dictionary mit 'in' und 'out' Listen der Wechsel
        """
        substitutions = {"in": [], "out": []}

        # Suche nach der Wechsel-Sektion
        sections = soup.find_all("section", class_="kick__section-item")
        for section in sections:
            header = section.find("header")
            if header and header.find("h4"):
                h4_text = header.find("h4").get_text().strip()
                if "Wechsel" in h4_text:
                    # Wechsel-Zellen extrahieren
                    sub_cells = section.find_all(
                        "div", class_="kick__substitutions__cell"
                    )

                    for cell in sub_cells:
                        # Prüfe ob Einwechslung oder Auswechslung
                        is_substitution_in = (
                            "kick__substitutions__cell--no-space"
                            in cell.get("class", [])
                        )

                        player_link = cell.find(
                            "a", class_="kick__substitutions__player"
                        )
                        time_elem = cell.find("div", class_="kick__substitutions__time")

                        if player_link:
                            player_name = self._clean_player_name(
                                player_link.get_text()
                            )
                            time_str = time_elem.get_text().strip() if time_elem else ""
                            minute = self._parse_time_to_minutes(time_str)

                            sub_data = {
                                "player": player_name,
                                "minute": minute,
                                "time_str": time_str,
                            }

                            if is_substitution_in:
                                substitutions["in"].append(sub_data)
                            else:
                                substitutions["out"].append(sub_data)
                    break

        return substitutions

    def _parse_time_to_minutes(self, time_str: str) -> int:
        """
        Konvertiert Zeitangaben zu Minuten

        Beispiele:
        "45'" -> 45
        "90' +5" -> 95
        "11'" -> 11
        """
        try:
            # Entferne Anführungszeichen und normalisiere
            clean_time = time_str.replace("'", "").strip()

            # Prüfe auf Nachspielzeit-Muster
            if "+" in clean_time:
                parts = clean_time.split("+")
                base_time = int(parts[0].strip())
                extra_time = int(parts[1].strip())
                return base_time + extra_time
            else:
                # Nur die Grundzeit
                match = re.search(r"(\d+)", clean_time)
                if match:
                    return int(match.group(1))
        except (ValueError, AttributeError):
            pass

        return 0

    def extract_team_names_from_url(self, url: str) -> Tuple[str, str]:
        """
        Extrahiert Teamnamen aus kicker.de URL

        Args:
            url: kicker.de Schema-URL

        Returns:
            Tuple (home_team, away_team)
        """
        try:
            # Muster: /team1-gegen-team2-jahr-bundesliga-id/schema
            pattern = r"/([^/]+)-gegen-([^/]+)-\d{4}-bundesliga"
            match = re.search(pattern, url)

            if match:
                home_team = match.group(1).replace("-", " ").title()
                away_team = match.group(2).replace("-", " ").title()

                # Bereinige häufige Team-Namen
                home_team = self._normalize_team_name(home_team)
                away_team = self._normalize_team_name(away_team)

                return home_team, away_team
        except Exception as e:
            print(f"⚠️ Fehler beim Extrahieren der Teamnamen: {e}")

        return "Unbekannt", "Unbekannt"

    def _normalize_team_name(self, team_name: str) -> str:
        """Normalisiert Team-Namen"""
        # Bekannte Ersetzungen für korrekte Schreibweise
        replacements = {
            "Muenchen": "München",
            "Bayern Muenchen": "Bayern München",
            "Fc Bayern Muenchen": "FC Bayern München",
            "Moenchengladbach": "Mönchengladbach",
            "Bor Moenchengladbach": "Bor. Mönchengladbach",
            "Koeln": "Köln",
            "Fc Koeln": "1. FC Köln",
            "Nuernberg": "Nürnberg",
            "Duesseldorf": "Düsseldorf",
            "Wuerzburg": "Würzburg",
        }

        return replacements.get(team_name, team_name)

    async def analyze_full_match(self, schema_url: str) -> Dict[str, any]:
        """
        Komplette Analyse einer Spielschema-Seite

        Args:
            schema_url: URL zur kicker.de Schema-Seite

        Returns:
            Dictionary mit allen extrahierten Daten
        """
        html_content = await self.fetch_schema_page(schema_url)
        if not html_content:
            return {}

        soup = BeautifulSoup(html_content, "html.parser")

        # Teams aus URL extrahieren
        home_team, away_team = self.extract_team_names_from_url(schema_url)

        # Alle Daten extrahieren
        goals = self.extract_goals_modern(soup)
        home_lineup, away_lineup = self.extract_lineups_modern(soup)
        substitutions = self.extract_substitutions_modern(soup)

        # Ergebnis berechnen
        home_score = len([g for g in goals if g["team"] == "home"])
        away_score = len([g for g in goals if g["team"] == "away"])

        return {
            "url": schema_url,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": home_score,
            "away_score": away_score,
            "goals": goals,
            "home_lineup": home_lineup,
            "away_lineup": away_lineup,
            "substitutions": substitutions,
            "extraction_success": {
                "goals": len(goals) > 0,
                "lineups": len(home_lineup) > 0 and len(away_lineup) > 0,
                "substitutions": len(substitutions["in"]) > 0
                or len(substitutions["out"]) > 0,
            },
        }

    async def close(self):
        """Schließt den HTTP-Client"""
        await self.client.aclose()


# Test-Funktionen
async def test_local_html_file():
    """Test mit der lokalen HTML-Datei"""
    print("🔍 Teste Parser mit lokaler HTML-Datei...")

    # Lade die lokale HTML-Datei
    html_file_path = r"c:\Users\yigit\OneDrive\Desktop\CODING\Backup Kicker.de\kicker v2.3 muster\html\Spielschema ｜ Bor. Mönchengladbach - Bayer 04 Leverkusen 2：3 ｜ 1. Spieltag ｜ Bundesliga 2024_25 - kicker (24.6.2025 12：03：57).html"

    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        parser = ModernKickerParser()
        soup = BeautifulSoup(html_content, "html.parser")

        # Tore extrahieren
        goals = parser.extract_goals_modern(soup)
        print(f"⚽ Tore gefunden: {len(goals)}")
        for goal in goals:
            print(
                f"  {goal['minute']}': {goal['scorer']} ({goal['team']}) - {goal['type']}"
            )

        # Aufstellungen extrahieren
        home_lineup, away_lineup = parser.extract_lineups_modern(soup)
        print(f"\n👥 Aufstellung Heim: {len(home_lineup)} Spieler")
        print(f"👥 Aufstellung Auswärts: {len(away_lineup)} Spieler")

        if home_lineup:
            print(
                f"   Heim: {', '.join(home_lineup[:5])}{'...' if len(home_lineup) > 5 else ''}"
            )
        if away_lineup:
            print(
                f"   Auswärts: {', '.join(away_lineup[:5])}{'...' if len(away_lineup) > 5 else ''}"
            )

        # Wechsel extrahieren
        substitutions = parser.extract_substitutions_modern(soup)
        print(f"\n🔄 Einwechslungen: {len(substitutions['in'])}")
        print(f"🔄 Auswechslungen: {len(substitutions['out'])}")

        await parser.close()

    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")


async def test_live_url():
    """Test mit einer Live-URL"""
    print("\n🌐 Teste Parser mit Live-URL...")

    parser = ModernKickerParser()
    try:
        # Test-URL - müsste angepasst werden für aktuelles Spiel
        test_url = "https://www.kicker.de/moenchengladbach-gegen-leverkusen-2024-bundesliga-4863077/schema"

        result = await parser.analyze_full_match(test_url)

        if result:
            print(f"🏟️ Spiel: {result['home_team']} vs {result['away_team']}")
            print(f"📊 Ergebnis: {result['home_score']}:{result['away_score']}")
            print(f"⚽ Tore: {len(result['goals'])}")
            print(
                f"👥 Aufstellungen: {len(result['home_lineup'])} vs {len(result['away_lineup'])}"
            )

            # Erfolg der Extraktion
            success = result["extraction_success"]
            print(f"✅ Erfolgreiche Extraktion:")
            print(f"   Tore: {'✓' if success['goals'] else '✗'}")
            print(f"   Aufstellungen: {'✓' if success['lineups'] else '✗'}")
            print(f"   Wechsel: {'✓' if success['substitutions'] else '✗'}")
        else:
            print("❌ Keine Daten extrahiert")

    except Exception as e:
        print(f"❌ Test-Fehler: {e}")
    finally:
        await parser.close()


if __name__ == "__main__":
    print("🚀 Kicker.de Modern Parser Test\n")
    asyncio.run(test_local_html_file())
    # Uncomment für Live-Test:
    # asyncio.run(test_live_url())
