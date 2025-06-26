"""
Verbesserter Kicker.de Scraper für robuste Extraktion von Torschützen und Aufstellungen
====================================================================================

Dieser Scraper implementiert die Erkenntnisse aus der HTML-Struktur-Analyse 2024/25
und bietet mehrfache Fallback-Strategien für maximale Robustheit.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import httpx
from models.game_data import GameData, Player, Goal, Team


class ImprovedKickerScraper:
    """
    Verbesserter Kicker.de Scraper mit robusten Parsing-Strategien
    für moderne kicker.de HTML-Strukturen (2024/25 und später)
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

    async def fetch_match_schema(self, schema_url: str) -> Optional[str]:
        """
        Lädt die HTML-Seite eines Spielschemas asynchron

        Args:
            schema_url: URL zur kicker.de Schema-Seite

        Returns:
            HTML-Content oder None bei Fehler
        """
        try:
            response = await self.client.get(schema_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Fehler beim Laden von {schema_url}: {e}")
            return None

    def extract_goal_scorers(self, soup: BeautifulSoup) -> List[Goal]:
        """
        Extrahiert Torschützen mit mehrfachen Fallback-Strategien

        Args:
            soup: BeautifulSoup-Objekt der Schema-Seite

        Returns:
            Liste der Tor-Objekte
        """
        goals = []

        # STRATEGIE 1: Moderner Ansatz (2024/25)
        goals.extend(self._extract_goals_modern(soup))

        # STRATEGIE 2: Fallback für ältere Strukturen
        if not goals:
            goals.extend(self._extract_goals_fallback(soup))

        # STRATEGIE 3: Letzter Ausweg - Regex-basiert
        if not goals:
            goals.extend(self._extract_goals_regex(soup))

        return goals

    def _extract_goals_modern(self, soup: BeautifulSoup) -> List[Goal]:
        """
        Extraktion basierend auf der modernen 2024/25 HTML-Struktur
        """
        goals = []

        # Primärer Selektor: Tore-Sektion finden
        tore_section = soup.find("section", class_="kick__section-item")
        if tore_section:
            header = tore_section.find("header")
            if header and header.find("h4") and "Tore" in header.find("h4").get_text():
                # Alle Tor-Ereignisse extrahieren
                goal_events = tore_section.find_all("div", class_="kick__goals")

                for goal_event in goal_events:
                    goal = self._parse_goal_event_modern(goal_event)
                    if goal:
                        goals.append(goal)

        return goals

    def _parse_goal_event_modern(self, goal_event: Tag) -> Optional[Goal]:
        """
        Parst ein einzelnes Tor-Ereignis in der modernen Struktur
        """
        try:
            # Zeit extrahieren
            time_elem = goal_event.find("span", class_="kick__goals__time")
            time_str = time_elem.get_text().strip() if time_elem else "0'"

            # Zeit normalisieren (z.B. "90' +11" -> 90+11)
            minute = self._parse_match_time(time_str)

            # Spieler extrahieren
            player_elem = goal_event.find("a", class_="kick__goals__player")
            if not player_elem:
                return None

            player_name_elem = player_elem.find(
                "span", class_="kick__substitutions--hide-mobile"
            )
            if not player_name_elem:
                player_name_elem = player_elem.find("span")

            if not player_name_elem:
                player_name = player_elem.get_text().strip()
            else:
                player_name = player_name_elem.get_text().strip()

            # Team bestimmen (links oder rechts)
            team_elem = goal_event.find("div", class_="kick__goals__team")
            is_home_team = (
                "kick__goals__team--left" in team_elem.get("class", [])
                if team_elem
                else True
            )

            # Tor-Art extrahieren
            assist_elem = goal_event.find("div", class_="kick__assist__player")
            goal_type = ""
            if assist_elem:
                type_span = assist_elem.find("span")
                if type_span:
                    goal_type = type_span.get_text().strip()

            return Goal(
                minute=minute, scorer=player_name, team=team_side, assist=goal_type
            )

        except Exception as e:
            print(f"Fehler beim Parsen des Tor-Ereignisses: {e}")
            return None

    def _extract_goals_fallback(self, soup: BeautifulSoup) -> List[Goal]:
        """
        Fallback-Strategie für ältere HTML-Strukturen
        """
        goals = []

        # Suche nach verschiedenen möglichen Tor-Containern
        goal_selectors = [
            ".kick__goals",
            '[class*="goal"]',
            '[class*="scorer"]',
            ".matchdata-goals",
            ".goals-list",
        ]

        for selector in goal_selectors:
            goal_elements = soup.select(selector)
            if goal_elements:
                for elem in goal_elements:
                    goal = self._parse_goal_fallback(elem)
                    if goal:
                        goals.append(goal)
                break  # Wenn wir Tore gefunden haben, stoppen

        return goals

    def _parse_goal_fallback(self, elem: Tag) -> Optional[Goal]:
        """
        Fallback-Parsing für Tor-Elemente
        """
        try:
            text = elem.get_text()

            # Regex für Zeit-Extraktion
            time_match = re.search(r"(\d{1,3})'?(?:\s*\+\s*(\d+))?", text)
            minute = 0
            if time_match:
                minute = int(time_match.group(1))
                if time_match.group(2):  # Nachspielzeit
                    minute += int(time_match.group(2))

            # Spielername extrahieren (verschiedene Ansätze)
            player_name = self._extract_player_name_fallback(elem, text)

            if not player_name:
                return None

            return Goal(
                minute=minute,
                player=player_name,
                team="home",  # Default, müsste durch Kontext bestimmt werden
                goal_type="",
            )

        except Exception:
            return None

    def _extract_player_name_fallback(self, elem: Tag, text: str) -> str:
        """
        Extrahiert Spielernamen mit verschiedenen Fallback-Methoden
        """
        # 1. Suche nach Links zu Spieler-Profilen
        player_link = elem.find("a", href=re.compile(r"/spieler/"))
        if player_link:
            return player_link.get_text().strip()

        # 2. Suche nach speziellen Klassen
        player_spans = elem.find_all("span", class_=re.compile(r"player|name"))
        if player_spans:
            return player_spans[0].get_text().strip()

        # 3. Regex-basierte Extraktion aus dem Text
        # Entferne Zeit-Angaben und häufige Zusätze
        clean_text = re.sub(r"\d{1,3}'(?:\s*\+\s*\d+)?", "", text)
        clean_text = re.sub(r"(Tor|Goal|Treffer)", "", clean_text, flags=re.IGNORECASE)
        clean_text = clean_text.strip()

        # Nimm das erste "Wort" als Spielername (vereinfacht)
        words = clean_text.split()
        if words:
            return words[0]

        return ""

    def _extract_goals_regex(self, soup: BeautifulSoup) -> List[Goal]:
        """
        Letzter Ausweg: Regex-basierte Extraktion aus dem gesamten Text
        """
        goals = []
        full_text = soup.get_text()

        # Regex für typische Tor-Patterns
        goal_patterns = [
            r"(\d{1,3})'?\s*([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*)",
            r"([A-ZÄÖÜ][a-zäöüß]+)\s+(\d{1,3})'",
        ]

        for pattern in goal_patterns:
            matches = re.finditer(pattern, full_text)
            for match in matches:
                try:
                    if pattern.startswith(r"(\d"):  # Zeit zuerst
                        minute = int(match.group(1))
                        player_name = match.group(2).strip()
                    else:  # Name zuerst
                        player_name = match.group(1).strip()
                        minute = int(match.group(2))

                    goals.append(
                        Goal(
                            minute=minute,
                            player=player_name,
                            team="home",  # Default
                            goal_type="",
                        )
                    )
                except (ValueError, IndexError):
                    continue

        return goals

    def extract_lineups(self, soup: BeautifulSoup) -> Tuple[List[Player], List[Player]]:
        """
        Extrahiert Aufstellungen beider Teams mit Fallback-Strategien

        Returns:
            Tuple (home_team_players, away_team_players)
        """
        # STRATEGIE 1: Moderne Struktur
        home_players, away_players = self._extract_lineups_modern(soup)

        # STRATEGIE 2: Fallback
        if not home_players and not away_players:
            home_players, away_players = self._extract_lineups_fallback(soup)

        return home_players, away_players

    def _extract_lineups_modern(
        self, soup: BeautifulSoup
    ) -> Tuple[List[Player], List[Player]]:
        """
        Extraktion der Aufstellungen basierend auf moderner HTML-Struktur
        """
        home_players = []
        away_players = []

        # Aufstellungs-Sektion finden
        lineup_section = soup.find("section", class_="kick__section-item")
        if lineup_section:
            header = lineup_section.find("header")
            if (
                header
                and header.find("h4")
                and "Aufstellung" in header.find("h4").get_text()
            ):

                # Linkes Team (Heimmannschaft)
                left_team = lineup_section.find(
                    "div", class_="kick__lineup__team--left"
                )
                if left_team:
                    home_players = self._parse_team_lineup(left_team)

                # Rechtes Team (Auswärtsmannschaft)
                right_team = lineup_section.find(
                    "div", class_="kick__lineup__team--right"
                )
                if right_team:
                    away_players = self._parse_team_lineup(right_team)

        return home_players, away_players

    def _parse_team_lineup(self, team_container: Tag) -> List[Player]:
        """
        Parst die Aufstellung eines Teams
        """
        players = []

        # Spieler-Links in der ungeordneten Liste finden
        lineup_list = team_container.find(
            "div", class_="kick__lineup-text__unorderedList"
        )
        if lineup_list:
            # Alle div-Elemente mit Spieler-Links
            player_divs = lineup_list.find_all("div")

            for div in player_divs:
                player_link = div.find("a", href=re.compile(r"/spieler/"))
                if player_link:
                    player_name = player_link.get_text().strip()

                    # Captain-Status prüfen
                    is_captain = bool(
                        div.find("span", class_="kick__icon-Captain_DICK")
                    )

                    # Bewertung extrahieren (falls vorhanden)
                    rating = ""
                    badge = div.find("span", class_="kick__badge--note")
                    if badge:
                        rating = badge.get_text().strip()

                    # Position bestimmen (vereinfacht über div-Position)
                    position = self._determine_position(div, len(players))

                    players.append(
                        Player(
                            name=player_name,
                            position=position,
                            is_captain=is_captain,
                            rating=rating,
                        )
                    )

        return players

    def _extract_lineups_fallback(
        self, soup: BeautifulSoup
    ) -> Tuple[List[Player], List[Player]]:
        """
        Fallback-Strategie für Aufstellungs-Extraktion
        """
        home_players = []
        away_players = []

        # Suche nach Spieler-Links
        player_links = soup.find_all("a", href=re.compile(r"/spieler/"))

        # Vereinfachte Aufteilung: erste Hälfte = Heimteam, zweite = Auswärtsteam
        mid_point = len(player_links) // 2

        for i, link in enumerate(player_links):
            player_name = link.get_text().strip()
            if player_name:  # Leere Namen ignorieren
                player = Player(
                    name=player_name, position="", is_captain=False, rating=""
                )

                if i < mid_point:
                    home_players.append(player)
                else:
                    away_players.append(player)

        return home_players, away_players

    def _determine_position(self, div: Tag, player_index: int) -> str:
        """
        Bestimmt die Position eines Spielers basierend auf der Reihenfolge
        """
        # Vereinfachte Positions-Zuordnung basierend auf typischen Aufstellungen
        if player_index == 0:
            return "TW"  # Torwart
        elif player_index in [1, 2, 3, 4]:
            return "AB"  # Abwehr
        elif player_index in [5, 6, 7, 8]:
            return "MF"  # Mittelfeld
        else:
            return "ST"  # Sturm

    def _parse_match_time(self, time_str: str) -> int:
        """
        Parst Zeitangaben wie "90'" oder "90' +11" zu Minuten
        """
        try:
            # Entferne Anführungszeichen und normalisiere
            time_str = time_str.replace("'", "").strip()

            # Prüfe auf Nachspielzeit
            if "+" in time_str:
                parts = time_str.split("+")
                base_time = int(parts[0].strip())
                extra_time = int(parts[1].strip())
                return base_time + extra_time
            else:
                return int(time_str)
        except (ValueError, IndexError):
            return 0

    async def parse_full_match_data(self, schema_url: str) -> Optional[GameData]:
        """
        Komplette Extraktion aller Spieldaten von einer Schema-URL

        Args:
            schema_url: URL zur kicker.de Schema-Seite

        Returns:
            GameData-Objekt oder None bei Fehler
        """
        html_content = await self.fetch_match_schema(schema_url)
        if not html_content:
            return None

        soup = BeautifulSoup(html_content, "html.parser")

        # Basis-Informationen extrahieren
        game_data = GameData()

        # Teams aus URL oder Title extrahieren
        game_data.home_team, game_data.away_team = self._extract_teams_from_url(
            schema_url
        )

        # Torschützen extrahieren
        goals = self.extract_goal_scorers(soup)
        game_data.goals = goals

        # Aufstellungen extrahieren
        home_lineup, away_lineup = self.extract_lineups(soup)
        game_data.home_lineup = home_lineup
        game_data.away_lineup = away_lineup

        # Ergebnis aus Torschützen berechnen
        home_goals = len([g for g in goals if g.team == "home"])
        away_goals = len([g for g in goals if g.team == "away"])
        game_data.home_score = home_goals
        game_data.away_score = away_goals

        return game_data

    def _extract_teams_from_url(self, url: str) -> Tuple[str, str]:
        """
        Extrahiert Teamnamen aus der URL

        Args:
            url: kicker.de Schema-URL

        Returns:
            Tuple (home_team, away_team)
        """
        try:
            # URL-Pattern: .../team1-gegen-team2-jahr-bundesliga-id/schema
            match = re.search(r"/([^/]+)-gegen-([^/]+)-\d{4}-bundesliga", url)
            if match:
                home_team = match.group(1).replace("-", " ").title()
                away_team = match.group(2).replace("-", " ").title()
                return home_team, away_team
        except Exception:
            pass

        return "Unbekannt", "Unbekannt"

    async def close(self):
        """Schließt den HTTP-Client"""
        await self.client.aclose()


# Test-Funktionen für die Entwicklung
async def test_improved_scraper():
    """Test-Funktion für den verbesserten Scraper"""
    scraper = ImprovedKickerScraper()

    try:
        # Test mit einer bekannten URL
        test_url = "https://www.kicker.de/moenchengladbach-gegen-leverkusen-2024-bundesliga-4863077/schema"

        print("🔄 Teste verbesserten Scraper...")
        game_data = await scraper.parse_full_match_data(test_url)

        if game_data:
            print(f"✅ Spiel: {game_data.home_team} vs {game_data.away_team}")
            print(f"📊 Ergebnis: {game_data.home_score}:{game_data.away_score}")
            print(f"⚽ Torschützen: {len(game_data.goals)}")
            print(f"👥 Aufstellung Heim: {len(game_data.home_lineup)}")
            print(f"👥 Aufstellung Auswärts: {len(game_data.away_lineup)}")

            # Details der Torschützen
            if game_data.goals:
                print("\n🥅 Torschützen:")
                for goal in game_data.goals:
                    print(f"  {goal.minute}': {goal.player} ({goal.team})")
        else:
            print("❌ Keine Daten extrahiert")

    except Exception as e:
        print(f"❌ Test-Fehler: {e}")
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(test_improved_scraper())
