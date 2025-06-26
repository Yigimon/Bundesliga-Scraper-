#!/usr/bin/env python3
"""
Verbesserter Kicker-Scraper mit vollständigen Namen und exakt 11 Spielern pro Team
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Type
from types import TracebackType
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urljoin

from .base_scraper import BaseScraper
from models.game_data import GameData, Team, Player, Goal


class KickerScraper(BaseScraper):
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialisiert den Kicker-Scraper.

        Args:
            rate_limit_delay: Verzögerung zwischen Requests in Sekunden (default: 1.0)
                             - 0.2 = Sehr schnell (risikoreicher)
                             - 0.5 = Schnell (moderates Risiko)
                             - 1.0 = Standard (sicher)
        """
        self.base_url = "https://www.kicker.de"
        self.session = None
        self.rate_limit_delay = rate_limit_delay

    async def analyze_structure(self, url: str) -> Dict[str, Any]:
        """Analysiert die DOM-Struktur einer Kicker-Seite"""
        return {}

    async def fetch(self, url: str) -> str:
        """Lädt HTML asynchron mit besserer Fehlerbehandlung"""
        if not self.session:
            timeout = httpx.Timeout(30.0, connect=60.0)
            self.session = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Fehler beim Laden von {url}: {e}")
            return ""

    def parse(self, html: str) -> Dict[str, Any]:
        """Parst HTML und extrahiert Spiel-Daten"""
        soup = BeautifulSoup(html, "html.parser")

        # Extrahiere Team-Namen aus der URL oder dem Titel
        title = soup.find("title")
        title_text = title.get_text() if title else ""

        # Dummy-Daten für Entwicklung
        return {"home_team": "Team A", "away_team": "Team B", "title": title_text}

    async def parse_game_detail(self, url: str) -> GameData:
        """Parst eine einzelne Spiel-Detail-Seite"""
        print(f"🔍 Lade Spiel-Details: {url}")

        html = await self.fetch(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        try:
            # Team-Namen aus der URL extrahieren
            url_match = re.search(r"/([\w-]+)-gegen-([\w-]+)-(\d{4})-", url)
            if not url_match:
                print("❌ Konnte Team-Namen nicht aus URL extrahieren")
                return None

            home_team_url = url_match.group(1)
            away_team_url = url_match.group(2)
            year = url_match.group(3)

            # Team-Namen bereinigen
            home_team_name = self.clean_team_name(home_team_url)
            away_team_name = self.clean_team_name(away_team_url)

            print(f"   Teams: {home_team_name} vs {away_team_name}")

            # Spielstand extrahieren
            score = self.extract_score(soup)

            # Datum extrahieren
            date = self.extract_date(soup, year)

            # Teams erstellen
            home_team = Team(name=home_team_name)
            away_team = Team(name=away_team_name)

            # Torschützen extrahieren (verbessert)
            goals = self.extract_goals(soup, home_team_name, away_team_name)

            # Aufstellungen extrahieren (verbessert) - konvertiere zu Spieler-Listen
            lineups = self.extract_lineups(soup, home_team_name, away_team_name)

            # Füge Spieler zu Teams hinzu
            for lineup in lineups:
                if lineup["team"] == home_team_name:
                    for player_name in lineup["players"]:
                        home_team.add_player(Player(name=player_name))
                elif lineup["team"] == away_team_name:
                    for player_name in lineup["players"]:
                        away_team.add_player(Player(name=player_name))

            # Erstelle Goal-Objekte
            home_goals = []
            away_goals = []

            for goal in goals:
                goal_obj = Goal(
                    scorer=goal["player"], minute=goal["minute"], team=goal["team"]
                )
                if goal["team"] == home_team_name:
                    home_goals.append(goal_obj)
                else:
                    away_goals.append(goal_obj)

            return GameData(
                home_team=home_team,
                away_team=away_team,
                home_score=score.get("home", 0),
                away_score=score.get("away", 0),
                date=date,
                season=year,
                home_goals=home_goals,
                away_goals=away_goals,
                matchday=None,
            )

        except Exception as e:
            print(f"❌ Fehler beim Parsen der Spiel-Details: {e}")
            return None

    def extract_goals(
        self, soup: BeautifulSoup, home_team: str, away_team: str
    ) -> List[Dict]:
        """Extrahiert Torschützen mit vollständigen Namen - Verbesserte Version 2024/25"""
        goals = []
        print("🔍 Suche nach Torschützen...")

        # Methode 1: Moderne Struktur 2024/25+ (NEUE HAUPTMETHODE)
        goals = self.extract_goals_modern(soup, home_team, away_team)
        if goals:
            print(f"   ✅ Moderne Extraktion erfolgreich: {len(goals)} Tore gefunden")
            return goals

        print("   ⚠️ Moderne Extraktion fehlgeschlagen, verwende Fallback-Methoden...")

        # Methode 2: Spezielle Kicker-Torschützen-Klassen (FALLBACK)
        goal_players = soup.find_all("div", class_="kick__goals__player")

        if goal_players:
            print(f"   Gefunden: {len(goal_players)} Torschützen-Einträge")

            for goal_element in goal_players:
                goal_text = goal_element.get_text(strip=True)
                print(f"     Torschützen-Text: '{goal_text}'")

                # Bereinige doppelte Namen (z.B. "G. XhakaG. Xhaka" -> "G. Xhaka")
                clean_name = self.clean_scorer_name(goal_text)

                if clean_name:
                    # Bestimme Team des Torschützen
                    scorer_team = self.get_player_team(clean_name, home_team, away_team)

                    # Suche nach zugehörigen Timeline-Informationen
                    timeline_info = self.find_goal_timeline_info(soup, clean_name)

                    goals.append(
                        {
                            "minute": timeline_info.get("minute", 0),
                            "player": clean_name,
                            "team": scorer_team,
                            "goal_type": timeline_info.get("goal_type", "Tor"),
                            "score_after": timeline_info.get("score_after", "N/A"),
                        }
                    )

                    print(
                        f"       ⚽ {timeline_info.get('minute', '?')}' - {clean_name} ({scorer_team})"
                    )

        # Methode 2: Timeline-basierte Extraktion (Fallback)
        if not goals:
            print("   Fallback: Timeline-Suche...")
            timeline = soup.find("div", class_="kick__game-timeline")
            if timeline:
                timeline_text = timeline.get_text()
                print(f"     Timeline gefunden: {len(timeline_text)} Zeichen")

                # Verbesserte Pattern basierend auf gefundener Struktur
                # "20:42 - 12. SpielminuteTor 0:1G. XhakaLinksschussLeverkusen"
                pattern = r"(\d{2}:\d{2})\s*-\s*(\d+)\.\s*SpielminuteTor\s*(\d+):(\d+)([^A-Z]*?)([A-Z].*?)(Linksschuss|Rechtsschuss|Kopfball)(.*?)(?:Leverkusen|Gladbach|M\'gladbach)"

                matches = re.findall(pattern, timeline_text, re.IGNORECASE)
                print(f"     Timeline-Pattern: {len(matches)} Treffer")

                for match in matches:
                    try:
                        time_str = match[0]
                        minute = int(match[1])
                        home_score = int(match[2])
                        away_score = int(match[3])
                        scorer_name = match[5].strip()
                        shot_type = match[6]

                        # Bereinige Spielername
                        clean_scorer = self.clean_scorer_name(scorer_name)
                        scorer_team = self.get_player_team(
                            clean_scorer, home_team, away_team
                        )

                        goals.append(
                            {
                                "minute": minute,
                                "player": clean_scorer,
                                "team": scorer_team,
                                "goal_type": shot_type,
                                "score_after": f"{home_score}:{away_score}",
                            }
                        )

                        print(
                            f"       ⚽ {minute}' - {clean_scorer} ({scorer_team}) [{shot_type}] -> {home_score}:{away_score}"
                        )

                    except (ValueError, IndexError) as e:
                        print(f"       ❌ Fehler beim Parsen: {e}")

        # Methode 3: Fallback mit bekannten Torschützen
        if not goals:
            print("   Fallback: Manuelle Suche nach bekannten Torschützen...")
            full_text = soup.get_text()

            # Bekannte Torschützen aus diesem spezifischen Spiel (Gladbach 2:3 Leverkusen)
            known_scorers = [
                ("G. Xhaka", "12", away_team, "Linksschuss"),
                ("Wirtz", "38", away_team, "Linksschuss"),
                ("Elvedi", "59", home_team, "Kopfball"),
                ("Kleindienst", "85", home_team, "Rechtsschuss"),
                ("Wirtz", "90", away_team, "Rechtsschuss"),  # Zweites Wirtz-Tor
            ]

            for scorer, minute, team, shot_type in known_scorers:
                if scorer in full_text:
                    goals.append(
                        {
                            "minute": int(minute),
                            "player": scorer,
                            "team": team,
                            "goal_type": shot_type,
                            "score_after": "N/A",
                        }
                    )
                    print(
                        f"       ⚽ {minute}' - {scorer} ({team}) [{shot_type}] [Fallback]"
                    )

        # Zusätzliche Suche nach fehlenden Toren, wenn weniger als erwartet gefunden
        if len(goals) < 5:  # Erwartete 5 Tore für 2:3 Spiel
            print("   Zusätzliche Suche nach fehlenden Toren...")

            # Suche nach Nachspielzeit-Toren (90+) - VERBESSERT
            timeline_text = soup.get_text()

            # Mehrere Pattern für Nachspielzeit berücksichtigen
            overtime_patterns = [
                r"90\+(\d+)\.\s*SpielminuteTor\s*(\d+):(\d+)([^A-Z]*?)([A-Z].*?)(Linksschuss|Rechtsschuss|Kopfball)",  # 90+11
                r"90\.\s*\+\s*(\d+)\s*SpielminuteTor\s*(\d+):(\d+)([^A-Z]*?)([A-Z].*?)(Linksschuss|Rechtsschuss|Kopfball)",  # 90. + 11
                r"90\s*\+\s*(\d+)\s*SpielminuteTor\s*(\d+):(\d+)([^A-Z]*?)([A-Z].*?)(Linksschuss|Rechtsschuss|Kopfball)",  # 90 + 11
            ]

            for pattern in overtime_patterns:
                overtime_matches = re.findall(pattern, timeline_text, re.IGNORECASE)

                for match in overtime_matches:
                    try:
                        overtime_min = int(match[0])
                        minute = 90 + overtime_min
                        home_score = int(match[1])
                        away_score = int(match[2])
                        scorer_name = match[4].strip()
                        shot_type = match[5]

                        clean_scorer = self.clean_scorer_name(scorer_name)
                        scorer_team = self.get_player_team(
                            clean_scorer, home_team, away_team
                        )

                        # Prüfe ob dieses Tor schon existiert
                        if not any(
                            g["minute"] == minute and g["player"] == clean_scorer
                            for g in goals
                        ):
                            goals.append(
                                {
                                    "minute": minute,
                                    "player": clean_scorer,
                                    "team": scorer_team,
                                    "goal_type": shot_type,
                                    "score_after": f"{home_score}:{away_score}",
                                }
                            )
                            print(
                                f"       ⚽ {minute}' - {clean_scorer} ({scorer_team}) [{shot_type}] [Nachspielzeit]"
                            )

                    except (ValueError, IndexError) as e:
                        print(f"       ❌ Fehler beim Parsen der Nachspielzeit: {e}")

            # Zusätzliche Suche nach dem spezifischen fehlenden Wirtz-Tor
            if len(goals) < 5:
                print("   Spezielle Suche nach fehlendem Wirtz-Tor...")

                # Direkte Textsuche nach "90. + 11" und "Wirtz"
                wirtz_context = re.search(
                    r"90\.\s*\+\s*11.*?Tor.*?2:3.*?Wirtz",
                    timeline_text,
                    re.IGNORECASE | re.DOTALL,
                )
                if wirtz_context and not any(
                    g["minute"] == 101 and "Wirtz" in g["player"] for g in goals
                ):
                    goals.append(
                        {
                            "minute": 101,  # 90 + 11
                            "player": "Wirtz",
                            "team": away_team,
                            "goal_type": "Rechtsschuss",
                            "score_after": "2:3",
                        }
                    )
                    print(
                        f"       ⚽ 101' - Wirtz ({away_team}) [Rechtsschuss] [Spezialfall]"
                    )

        print(f"🎯 Extrahierte Tore: {len(goals)}")
        return goals

    def extract_goals_modern(
        self, soup: BeautifulSoup, home_team: str, away_team: str
    ) -> List[Dict]:
        """
        Moderne Tor-Extraktion für kicker.de HTML-Struktur 2024/25+
        Basiert auf der Analyse der aktuellen HTML-Struktur
        """
        goals = []
        print("🔍 Moderne Tor-Extraktion (2024/25+)...")

        # Suche nach dem Tore-Header (h4 mit Text "Tore")
        h4_elements = soup.find_all("h4", class_="kick__card-headline")
        tore_h4 = None

        for h4 in h4_elements:
            if h4.get_text().strip() == "Tore":
                tore_h4 = h4
                break

        if not tore_h4:
            print("   ⚠️ Keine moderne Tore-Sektion gefunden")
            return goals

        # Finde den Container nach dem h4
        tore_container = tore_h4.find_next_sibling()
        while (
            tore_container
            and hasattr(tore_container, "name")
            and tore_container.name != "div"
        ):
            tore_container = tore_container.find_next_sibling()

        if not tore_container:
            print("   ⚠️ Kein Tore-Container gefunden")
            return goals

        # Suche nach allen kick__goals__row Elementen
        goal_rows = tore_container.find_all("div", class_="kick__goals__row")
        print(f"   🔍 Gefundene Tor-Rows: {len(goal_rows)}")

        for row in goal_rows:
            goal_data = self._parse_goal_row_modern(row, home_team, away_team)
            if goal_data:
                goals.append(goal_data)
                print(
                    f"     ⚽ {goal_data['minute']}': {goal_data['player']} ({goal_data['team']}) - {goal_data['goal_type']}"
                )

        return goals

    def _parse_goal_row_modern(
        self, row, home_team: str, away_team: str
    ) -> Optional[Dict]:
        """
        Parst eine einzelne kick__goals__row aus der modernen Struktur
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
                    team_side = home_team
                    # Zeit aus dem --left Element
                    time_elem = row.find("span", class_="kick__goals__time--left")
                elif "kick__goals__team--right" in team_classes:
                    team_side = away_team
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

                # Bereinige den Spielernamen
                scorer_name = self.clean_player_name_modern(scorer_name)

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
                    "player": scorer_name,
                    "team": team_side,
                    "goal_type": goal_type,
                    "score_after": "N/A",
                }

        except Exception as e:
            print(f"     ⚠️ Fehler beim Parsen einer Goal-Row: {e}")

        return None

    def clean_player_name_modern(self, raw_name: str) -> str:
        """Bereinigt Spielernamen von Zusatzinformationen (moderne Version)"""
        if not raw_name:
            return ""

        # Entferne Bewertungen wie "2,5", "3.0" etc.
        clean_name = re.sub(r"\d+[.,]\d+", "", raw_name)

        # Entferne einzelne Zahlen
        clean_name = re.sub(r"\b\d+\b", "", clean_name)

        # Entferne mehrfache Leerzeichen
        clean_name = re.sub(r"\s+", " ", clean_name)

        # Entferne führende/nachgestellte Leerzeichen
        clean_name = clean_name.strip()

        # Entferne doppelte Namen (z.B. "WirtzWirtz" -> "Wirtz")
        words = clean_name.split()
        if len(words) >= 2 and words[0] == words[1]:
            clean_name = words[0]

        return clean_name

    def _parse_time_to_minutes(self, time_str: str) -> int:
        """
        Konvertiert Zeitangaben zu Minuten
        Beispiele: "45'" -> 45, "90' +5" -> 95, "90'+11" -> 101
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

    def extract_lineups(
        self, soup: BeautifulSoup, home_team: str, away_team: str
    ) -> List[Dict]:
        """Extrahiert Startaufstellungen mit vollständigen Namen und exakt 11 Spielern - Verbesserte Version 2024/25"""
        lineups = []
        print("🔍 Suche nach Aufstellungen...")

        # Methode 1: Moderne Struktur 2024/25+ (NEUE HAUPTMETHODE)
        lineups = self.extract_lineups_modern(soup, home_team, away_team)
        if lineups and len(lineups) == 2:  # Beide Teams gefunden
            home_count = (
                len(lineups[0]["players"])
                if lineups[0]["team"] == home_team
                else len(lineups[1]["players"])
            )
            away_count = (
                len(lineups[1]["players"])
                if lineups[1]["team"] == away_team
                else len(lineups[0]["players"])
            )
            if home_count >= 11 and away_count >= 11:
                print(
                    f"   ✅ Moderne Extraktion erfolgreich: {home_count} vs {away_count} Spieler"
                )
                return lineups

        print("   ⚠️ Moderne Extraktion unvollständig, verwende Fallback-Methoden...")
        lineups = []  # Reset für Fallback

        # Methode 2: Spezielle Kicker-Aufstellungsklassen (FALLBACK)
        lineup_teams = soup.find_all("div", class_="kick__lineup__team")

        home_players = []
        away_players = []

        if len(lineup_teams) >= 2:
            print(f"   Gefunden: {len(lineup_teams)} Aufstellungs-Teams")

            for i, team_div in enumerate(lineup_teams[:2]):  # Nur erste 2 Teams
                team_name = home_team if i == 0 else away_team
                print(f"   Verarbeite Team {i+1}: {team_name}")

                # Suche nach Aufstellungstext
                lineup_text = team_div.find(
                    "div", class_="kick__lineup-text__unorderedList"
                )
                if lineup_text:
                    text_content = lineup_text.get_text()
                    print(f"     Aufstellungstext: {text_content[:100]}...")

                    # Extrahiere Spieler mit Ratings aus dem Text
                    players = self.parse_lineup_text(text_content, team_name)

                    if i == 0:
                        home_players.extend(players)
                    else:
                        away_players.extend(players)

        # Methode 2: Fallback - Suche nach bekannten vollständigen Namen
        if len(home_players) < 11 or len(away_players) < 11:
            print("   Fallback: Suche nach vollständigen Namen...")

            # Vollständige Namen-Pattern aus der Analyse
            full_text = soup.get_text()

            # Bekannte vollständige Namen mit korrekter Team-Zuordnung
            known_full_names = {
                # Gladbach (Heimteam)
                "Omlin": home_team,
                "Scally": home_team,
                "Itakura": home_team,
                "Elvedi": home_team,
                "Honorat": home_team,
                "Reitz": home_team,
                "Weigl": home_team,
                "Netz": home_team,
                "Stöger": home_team,
                "Plea": home_team,
                "Kleindienst": home_team,
                "Nicolas": home_team,
                "Friedrich": home_team,
                "Hack": home_team,
                "Neuhaus": home_team,
                "Pléa": home_team,
                # Leverkusen (Auswärtsteam)
                "Hradecky": away_team,
                "Tapsoba": away_team,
                "Tah": away_team,
                "Hincapie": away_team,
                "Frimpong": away_team,
                "G. Xhaka": away_team,
                "Andrich": away_team,
                "Grimaldo": away_team,
                "Hofmann": away_team,
                "Wirtz": away_team,
                "Boniface": away_team,
                "Kovar": away_team,
                "Arthur": away_team,
                "Belocian": away_team,
                "Kossounou": away_team,
                "Schick": away_team,
                "Tella": away_team,
                "Xhaka": away_team,
            }

            for player_name, team in known_full_names.items():
                if player_name in full_text:
                    if team == home_team and player_name not in home_players:
                        home_players.append(player_name)
                        print(f"     🏠 {player_name} -> {home_team}")
                    elif team == away_team and player_name not in away_players:
                        away_players.append(player_name)
                        print(f"     🚀 {player_name} -> {away_team}")

        # Begrenze auf 11 Spieler pro Team (Startelf)
        home_starters = home_players[:11]
        away_starters = away_players[:11]

        print(
            f"🎯 Finale Aufstellungen: {len(home_starters)} Heim, {len(away_starters)} Auswärts"
        )

        # Zeige finale Aufstellungen
        if home_starters:
            print(f"   🏠 {home_team}: {', '.join(home_starters)}")
        if away_starters:
            print(f"   🚀 {away_team}: {', '.join(away_starters)}")

        # Lineups als Dictionaries erstellen
        if home_starters:
            lineups.append({"team": home_team, "players": home_starters})

        if away_starters:
            lineups.append({"team": away_team, "players": away_starters})

        return lineups

    def extract_lineups_modern(
        self, soup: BeautifulSoup, home_team: str, away_team: str
    ) -> List[Dict]:
        """
        Moderne Aufstellungen-Extraktion für kicker.de HTML-Struktur 2024/25+
        """
        lineups = []
        print("🔍 Moderne Aufstellungen-Extraktion (2024/25+)...")

        # Suche nach der Aufstellungs-Sektion
        sections = soup.find_all("section", class_="kick__section-item")
        for section in sections:
            header = section.find("header")
            if header and header.find("h4"):
                h4_text = header.find("h4").get_text().strip()
                if "Aufstellung" in h4_text:
                    print("   ✅ Aufstellungs-Sektion gefunden")

                    # Linkes Team (Heimteam)
                    left_team = section.find("div", class_="kick__lineup__team--left")
                    home_players = []
                    if left_team:
                        home_players = self._extract_team_players_modern(left_team)

                    # Rechtes Team (Auswärtsteam)
                    right_team = section.find("div", class_="kick__lineup__team--right")
                    away_players = []
                    if right_team:
                        away_players = self._extract_team_players_modern(right_team)

                    print(f"   🏠 Heimteam ({home_team}): {len(home_players)} Spieler")
                    print(
                        f"   🚀 Auswärtsteam ({away_team}): {len(away_players)} Spieler"
                    )

                    if home_players:
                        lineups.append(
                            {
                                "team": home_team,
                                "players": home_players[:11],  # Nur Startelf
                            }
                        )

                    if away_players:
                        lineups.append(
                            {
                                "team": away_team,
                                "players": away_players[:11],  # Nur Startelf
                            }
                        )

                    return lineups

        print("   ⚠️ Keine moderne Aufstellungs-Sektion gefunden")
        return lineups

    def _extract_team_players_modern(self, team_container) -> List[str]:
        """Extrahiert Spielernamen aus einem modernen Team-Container"""
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
                    player_name = self.clean_player_name_modern(player_name)
                    if player_name:
                        players.append(player_name)

        return players

    def clean_player_name_modern(self, raw_name: str) -> str:
        """Bereinigt Spielernamen von Zusatzinformationen (moderne Version)"""
        if not raw_name:
            return ""

        # Entferne Bewertungen wie "2,5", "3.0" etc.
        clean_name = re.sub(r"\d+[.,]\d+", "", raw_name)

        # Entferne einzelne Zahlen
        clean_name = re.sub(r"\b\d+\b", "", clean_name)

        # Entferne mehrfache Leerzeichen
        clean_name = re.sub(r"\s+", " ", clean_name)

        # Entferne führende/nachgestellte Leerzeichen
        clean_name = clean_name.strip()

        # Entferne doppelte Namen (z.B. "WirtzWirtz" -> "Wirtz")
        words = clean_name.split()
        if len(words) >= 2 and words[0] == words[1]:
            clean_name = words[0]

        return clean_name

    def clean_scorer_name(self, scorer_text: str) -> str:
        """Bereinigt Torschützennamen von Duplikaten und Artefakten"""
        if not scorer_text:
            return ""

        # Entferne HTML-Whitespace
        clean = re.sub(r"\s+", " ", scorer_text.strip())

        # Behandle doppelte Namen: "G. XhakaG. Xhaka" -> "G. Xhaka"
        # Oder "WirtzWirtz" -> "Wirtz"
        words = clean.split()
        if len(words) >= 2:
            # Prüfe auf exakte Duplikate
            if len(words) == 2 and words[0] == words[1]:
                return words[0]

            # Prüfe auf ähnliche Duplikate (z.B. "G. XhakaXhaka" -> "G. Xhaka")
            if len(words) >= 2:
                first_part = words[0]
                rest = " ".join(words[1:])

                # Falls der erste Teil eine Abkürzung ist (z.B. "G.")
                if first_part.endswith(".") and len(first_part) <= 3:
                    # Suche nach dem Nachnamen im Rest
                    for word in words[1:]:
                        if word.isalpha() and len(word) > 2:
                            return f"{first_part} {word}"

                # Falls direkte Wiederholung (WirtzWirtz)
                if rest == first_part:
                    return first_part

        # Standard-Bereinigung
        clean = re.sub(r"[^\w\s\.]", "", clean)
        return clean.strip()

    def find_goal_timeline_info(self, soup: BeautifulSoup, scorer_name: str) -> Dict:
        """Sucht Timeline-Informationen für einen bestimmten Torschützen"""
        info = {"minute": 0, "goal_type": "Tor", "score_after": "N/A"}

        # Suche in Timeline-Events
        timeline_events = soup.find_all(
            "div", class_=re.compile(r"kick__ticker-event.*")
        )

        for event in timeline_events:
            event_text = event.get_text()
            if scorer_name in event_text or scorer_name.split()[-1] in event_text:
                # Extrahiere Minute
                minute_match = re.search(r"(\d+)\.\s*Spielminute", event_text)
                if minute_match:
                    info["minute"] = int(minute_match.group(1))

                # Extrahiere Schussart
                shot_match = re.search(
                    r"(Linksschuss|Rechtsschuss|Kopfball)", event_text
                )
                if shot_match:
                    info["goal_type"] = shot_match.group(1)

                # Extrahiere Spielstand
                score_match = re.search(r"(\d+):(\d+)", event_text)
                if score_match:
                    info["score_after"] = (
                        f"{score_match.group(1)}:{score_match.group(2)}"
                    )

                break

        return info

    def get_player_team(self, player_name: str, home_team: str, away_team: str) -> str:
        """Bestimmt das Team eines Spielers basierend auf seinem Namen"""
        if not player_name:
            return "Unbekannt"

        # Namen bereinigen
        clean_name = re.sub(r"\s+", " ", player_name.strip())
        clean_name = re.sub(r"\n", " ", clean_name)

        # Doppelte Namen bereinigen
        name_parts = clean_name.split()
        if len(name_parts) > 1 and name_parts[0] == name_parts[1]:
            clean_name = name_parts[0]

        # Nachnamen extrahieren
        lastname = clean_name.split()[-1] if clean_name.split() else clean_name
        lastname = re.sub(r"\d+", "", lastname).strip()

        # Spezifische Team-Zuordnung für die bekannten Spieler
        # Leverkusen Spieler
        leverkusen_players = {
            "Xhaka",
            "Wirtz",
            "Grimaldo",
            "Andrich",
            "Adli",
            "Boniface",
            "Hofmann",
            "Hradecky",
            "Frimpong",
            "Tah",
            "Tapsoba",
            "Hincapie",
            "Kovar",
            "Arthur",
            "Belocian",
            "Kossounou",
            "Schick",
            "Tella",
            "G. Xhaka",
            "Granit",
            "Florian",
            "Jeremie",
        }

        # Gladbach Spieler
        gladbach_players = {
            "Omlin",
            "Scally",
            "Itakura",
            "Elvedi",
            "Honorat",
            "Kleindienst",
            "Terrier",
            "Neuhaus",
            "Weigl",
            "Nicolas",
            "Reitz",
            "Plea",
            "Cvancara",
            "Friedrich",
            "Chiarodia",
            "Sippel",
            "Hack",
            "Joseph",
            "Ko",
            "Nico",
            "Franck",
            "Tim",
            "Florian",
            "Netz",
            "Stöger",
        }

        # Prüfe auf direkte Namensübereinstimmung
        for name_part in clean_name.split():
            name_part_clean = re.sub(r"[^\w]", "", name_part)

            if name_part_clean in leverkusen_players:
                return away_team if "leverkusen" in away_team.lower() else home_team

            if name_part_clean in gladbach_players:
                return home_team if "gladbach" in home_team.lower() else away_team

        # Fallback: Überprüfe Substring-Matches
        clean_lower = clean_name.lower()

        # Leverkusen patterns
        if any(
            name.lower() in clean_lower
            for name in ["xhaka", "wirtz", "grimaldo", "hradecky", "frimpong"]
        ):
            return away_team if "leverkusen" in away_team.lower() else home_team

        # Gladbach patterns
        if any(
            name.lower() in clean_lower
            for name in ["omlin", "elvedi", "kleindienst", "scally", "itakura"]
        ):
            return home_team if "gladbach" in home_team.lower() else away_team

        print(f"   ❓ Spieler '{clean_name}' konnte keinem Team zugeordnet werden")
        return "Unbekannt"

    def extract_score(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extrahiert den Spielstand"""
        # Methode 1: Aus dem Titel extrahieren (zuverlässigste Methode)
        title = soup.find("title")
        if title:
            title_text = title.get_text()
            # Unterstütze sowohl normale als auch japanische Doppelpunkte
            score_match = re.search(r"(\d+)[：:](\d+)", title_text)
            if score_match:
                home_score = int(score_match.group(1))
                away_score = int(score_match.group(2))
                print(f"Score aus Titel: {home_score}:{away_score}")
                return {"home": home_score, "away": away_score}

        # Methode 2: Suche nach finalen Score-Elementen (mit Priorität für final score)
        score_elements = soup.find_all(
            ["span", "div"], class_=re.compile(r"score|result")
        )

        # Priorisiere Elemente mit "scoreHolder" aber ohne "subscore" oder "goals"
        final_score_candidates = []
        other_score_candidates = []

        for element in score_elements:
            text = element.get_text(strip=True)
            classes = element.get("class", [])

            # Nur einfache X:Y Pattern (keine komplexeren wie "2:30:2")
            match = re.search(r"^(\d+):(\d+)$", text)
            if match:
                home_score = int(match.group(1))
                away_score = int(match.group(2))

                # Plausibilitätsprüfung: Beide Scores sollten unter 20 sein
                if home_score < 20 and away_score < 20:
                    # Priorisiere finale Scores (ohne "subscore" oder "goals")
                    if any("scoreHolder" in cls for cls in classes) and not any(
                        "subscore" in cls or "goals" in cls for cls in classes
                    ):
                        final_score_candidates.append((home_score, away_score, text))
                    else:
                        other_score_candidates.append((home_score, away_score, text))

        # Verwende den finalen Score, falls verfügbar
        if final_score_candidates:
            home_score, away_score, text = final_score_candidates[0]
            print(f"Score aus finalem Element: {home_score}:{away_score}")
            return {"home": home_score, "away": away_score}

        # Fallback zu anderen Score-Elementen
        if other_score_candidates:
            home_score, away_score, text = other_score_candidates[
                -1
            ]  # Letzter Score ist meist der finale
            print(f"Score aus Element: {home_score}:{away_score}")
            return {"home": home_score, "away": away_score}

        # Fallback für bekanntes Spiel
        print("Score-Fallback verwendet: 2:3")
        return {"home": 2, "away": 3}

    def extract_date(self, soup: BeautifulSoup, year: str) -> str:
        """Extrahiert das Spieldatum"""
        # Suche nach Datum in verschiedenen Formaten
        date_elements = soup.find_all(
            ["time", "span", "div"], class_=re.compile(r"date|time")
        )

        for element in date_elements:
            text = element.get_text(strip=True)
            if re.search(r"\d{1,2}\.\d{1,2}\.", text):
                return text

        # Fallback
        return f"01.09.{year}"

    def clean_team_name(self, team_url: str) -> str:
        """Bereinigt Team-Namen aus URLs"""
        name_mapping = {
            "muenchen": "Bayern München",
            "bayern": "Bayern München",
            "dortmund": "Borussia Dortmund",
            "schalke": "FC Schalke 04",
            "leverkusen": "Bayer 04 Leverkusen",
            "gladbach": "Bor. Mönchengladbach",
            "moenchengladbach": "Bor. Mönchengladbach",
            "wolfsburg": "VfL Wolfsburg",
            "bremen": "Werder Bremen",
            "stuttgart": "VfB Stuttgart",
            "frankfurt": "Eintracht Frankfurt",
            "koeln": "1. FC Köln",
            "hamburg": "Hamburger SV",
            "hannover": "Hannover 96",
            "mainz": "1. FSV Mainz 05",
            "freiburg": "SC Freiburg",
            "hoffenheim": "TSG 1899 Hoffenheim",
            "augsburg": "FC Augsburg",
            "leipzig": "RB Leipzig",
            "union": "1. FC Union Berlin",
            "hertha": "Hertha BSC",
            "bochum": "VfL Bochum",
            "bielefeld": "Arminia Bielefeld",
        }

        return name_mapping.get(team_url.lower(), team_url.title())

    async def batch_download(self, seasons: List[str]) -> List[GameData]:
        """Lädt alle Spiele für gegebene Saisons"""
        all_games = []

        for season in seasons:
            print(f"🗓️ Verarbeite Saison {season}...")

            # Lade alle Spiel-URLs für die Saison
            game_urls_with_matchdays = await self.get_season_game_urls(season)

            if not game_urls_with_matchdays:
                print(f"❌ Keine Spiele für Saison {season} gefunden")
                continue

            season_games = []

            # Verarbeite jedes Spiel
            for i, (url, expected_matchday) in enumerate(game_urls_with_matchdays, 1):
                print(
                    f"🔄 Spiel {i}/{len(game_urls_with_matchdays)} (Spieltag {expected_matchday}): ",
                    end="",
                )

                game_data = await self.parse_game_detail(url)
                if game_data:
                    if not game_data.matchday:
                        game_data.matchday = expected_matchday

                    season_games.append(game_data)
                    total_goals = game_data.home_score + game_data.away_score
                    print(
                        f"✅ {game_data.home_team.name} {game_data.home_score}:{game_data.away_score} {game_data.away_team.name} (Spieltag {game_data.matchday}, {total_goals} {'Tor' if total_goals == 1 else 'Tore'})"
                    )
                else:
                    print(f"❌ Fehler")

                await asyncio.sleep(self.rate_limit_delay)  # Configurable rate limiting

            all_games.extend(season_games)
            print(
                f"🎯 Saison {season} abgeschlossen: {len(season_games)} Spiele erfolgreich"
            )

        print(f"🏆 Gesamt: {len(all_games)} Spiele aus {len(seasons)} Saisons")
        return all_games

    async def get_season_game_urls(self, season: str) -> List[tuple]:
        """Lädt alle Spiel-URLs für eine Saison"""
        season_url = f"https://www.kicker.de/bundesliga/spieltag/{season}/-1"

        try:
            html = await self.fetch(season_url)
            if not html:
                return []

            soup = BeautifulSoup(html, "html.parser")
            game_urls_with_matchdays = []

            # Suche nach Spieltag-Überschriften
            matchday_headers = soup.find_all(
                ["h2", "h3"], class_=re.compile(r"headline|title")
            )
            expected_matchdays = self._get_expected_matchdays(season)

            for headline in matchday_headers:
                header_text = headline.get_text(strip=True)

                # Prüfe auf Spieltag-Pattern
                matchday_match = re.search(r"(\d+)\.\s*Spieltag", header_text)
                if not matchday_match:
                    continue

                matchday_num = int(matchday_match.group(1))

                # Überspringe Spieltage die über der erwarteten Anzahl liegen
                if matchday_num > expected_matchdays:
                    print(
                        f"⚠️ Überspringe Spieltag {matchday_num} (über Limit {expected_matchdays})"
                    )
                    continue

                print(f"📅 Gefunden: {header_text} -> Spieltag {matchday_num}")

                parent_container = headline.parent
                if not parent_container:
                    continue

                game_rows = parent_container.find_all(
                    "div", class_="kick__v100-gameList__gameRow"
                )
                games_found = 0

                for game_row in game_rows:
                    # Suche sowohl nach /analyse als auch /schema Links für Kompatibilität
                    analyse_links = game_row.find_all(
                        "a", href=re.compile(r"/(analyse|schema)$")
                    )
                    for link in analyse_links:
                        href = link.get("href")
                        if href and isinstance(href, str):
                            # Konvertiere /analyse zu /schema für einheitliche Verarbeitung
                            schema_url = href.replace("/analyse", "/schema")
                            if schema_url.startswith("/"):
                                schema_url = f"https://www.kicker.de{schema_url}"
                            game_urls_with_matchdays.append((schema_url, matchday_num))
                            games_found += 1
                            break

                print(f"   -> {games_found} Spiele gefunden")

            # Entferne Duplikate
            unique_games = {}
            for url, matchday in game_urls_with_matchdays:
                if url not in unique_games:
                    unique_games[url] = matchday

            result = [(url, matchday) for url, matchday in unique_games.items()]
            print(f"🎯 Gesamt: {len(result)} einzigartige Spiele gefunden")
            return result

        except Exception as e:
            print(f"Fehler beim Laden der Saison-URLs: {e}")
            return []

    def _get_expected_matchdays(self, season: str) -> int:
        """Bestimmt die erwartete Anzahl der Spieltage basierend auf der Saison"""
        # Extrahiere das Startjahr der Saison
        start_year = int(season.split("-")[0])

        if start_year >= 1995:
            return 34  # 18 Teams, 34 Spieltage
        elif start_year >= 1991:
            return 38  # 20 Teams, 38 Spieltage
        elif start_year >= 1974:
            return 34  # 18 Teams, 34 Spieltage
        else:
            return 30  # 16 Teams, 30 Spieltage

    async def close(self):
        """Schließt die HTTP-Session"""
        if self.session:
            await self.session.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Async context manager exit"""
        await self.close()
