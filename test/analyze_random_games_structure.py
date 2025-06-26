"""
Analysiert zufällige Spiele von 1963-2025 um HTML-Strukturen für Aufstellungen und Tore zu verstehen.
Ziel: Redundante Parsing-Strategien für robuste Extraktion entwickeln.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import json
import random
from typing import Dict, List, Any
import time
from pathlib import Path


class RandomGameStructureAnalyzer:
    def __init__(self):
        self.client = None
        self.results = []

    async def setup_client(self):
        """Setup HTTP client mit realistischen Headers"""
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "de-DE,de;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            timeout=30.0,
        )

    async def get_random_seasons(self) -> List[str]:
        """Erstellt Liste von zufälligen Saisons zwischen 1963-2025"""
        seasons = []

        # Frühe Jahre (1963-1980)
        early_years = [f"{year}-{str(year+1)[-2:]}" for year in range(1963, 1981)]
        seasons.extend(random.sample(early_years, 3))

        # Mittlere Jahre (1981-2000)
        middle_years = [f"{year}-{str(year+1)[-2:]}" for year in range(1981, 2001)]
        seasons.extend(random.sample(middle_years, 3))

        # Moderne Jahre (2001-2020)
        modern_years = [f"{year}-{str(year+1)[-2:]}" for year in range(2001, 2021)]
        seasons.extend(random.sample(modern_years, 3))

        # Sehr moderne Jahre (2021-2025)
        recent_years = [f"{year}-{str(year+1)[-2:]}" for year in range(2021, 2025)]
        seasons.extend(random.sample(recent_years, 2))

        return seasons

    async def get_random_games_from_season(
        self, season: str, max_games: int = 3
    ) -> List[str]:
        """Holt zufällige Spiele einer Saison"""
        try:
            # Erst alle Spiele der Saison laden
            season_url = f"https://www.kicker.de/bundesliga/spieltag/{season}/-1"
            print(f"Lade Saison {season}: {season_url}")

            response = await self.client.get(season_url)
            if response.status_code != 200:
                print(f"Fehler beim Laden der Saison {season}: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            # Verschiedene Selektoren für Spiellinks probieren
            game_links = []

            # Moderne Struktur
            links = soup.find_all("a", href=True)
            for link in links:
                href = link.get("href", "")
                if "/bundesliga-" in href and "/schema" not in href:
                    if href.startswith("/"):
                        href = f"https://www.kicker.de{href}"
                    game_links.append(href)

            # Falls keine gefunden, andere Selektoren probieren
            if not game_links:
                # Ältere Struktur
                result_links = soup.find_all(
                    "a", class_=lambda x: x and "kick__" in x if x else False
                )
                for link in result_links:
                    href = link.get("href", "")
                    if "bundesliga" in href and "schema" not in href:
                        if href.startswith("/"):
                            href = f"https://www.kicker.de{href}"
                        game_links.append(href)

            # Duplikate entfernen
            game_links = list(set(game_links))

            # Zufällige Auswahl
            if len(game_links) > max_games:
                game_links = random.sample(game_links, max_games)

            print(f"Gefunden {len(game_links)} Spiele für Saison {season}")
            return game_links[:max_games]

        except Exception as e:
            print(f"Fehler beim Laden der Saison {season}: {e}")
            return []

    async def analyze_game_schema(self, game_url: str) -> Dict[str, Any]:
        """Analysiert die Schema-Seite eines Spiels"""
        try:
            # Schema-URL konstruieren
            if "/schema" not in game_url:
                schema_url = f"{game_url.rstrip('/')}/schema"
            else:
                schema_url = game_url

            print(f"Analysiere Spiel: {schema_url}")

            response = await self.client.get(schema_url)
            if response.status_code != 200:
                print(f"Fehler beim Laden des Spiels: {response.status_code}")
                return {}

            soup = BeautifulSoup(response.text, "html.parser")

            # Spiel-Info extrahieren
            title = soup.find("title")
            game_title = title.text if title else "Unbekannt"

            analysis = {
                "url": schema_url,
                "title": game_title,
                "lineup_structures": self.analyze_lineup_structures(soup),
                "goal_structures": self.analyze_goal_structures(soup),
                "raw_html_samples": self.extract_html_samples(soup),
            }

            return analysis

        except Exception as e:
            print(f"Fehler bei der Spielanalyse {game_url}: {e}")
            return {}

    def analyze_lineup_structures(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analysiert verschiedene Aufstellungs-Strukturen"""
        structures = {}

        # 1. Moderne kick__lineup Struktur
        lineup_teams = soup.find_all(
            class_=lambda x: x and "kick__lineup__team" in x if x else False
        )
        structures["kick__lineup__team"] = {"count": len(lineup_teams), "samples": []}

        for i, team in enumerate(lineup_teams[:2]):  # Max 2 Teams
            players = team.find_all(
                class_=lambda x: (
                    x and any(keyword in x for keyword in ["player", "name"])
                    if x
                    else False
                )
            )
            structures["kick__lineup__team"]["samples"].append(
                {
                    "team_index": i,
                    "player_count": len(players),
                    "player_classes": [
                        p.get("class", []) for p in players[:5]
                    ],  # Sample der ersten 5
                    "player_texts": [p.get_text(strip=True) for p in players[:5]],
                }
            )

        # 2. Tabellen-basierte Aufstellungen
        lineup_tables = soup.find_all("table")
        table_lineups = []
        for table in lineup_tables:
            if (
                "aufstellung" in table.get_text().lower()
                or len(table.find_all("tr")) > 10
            ):
                rows = table.find_all("tr")
                table_lineups.append(
                    {
                        "row_count": len(rows),
                        "sample_rows": [row.get_text(strip=True) for row in rows[:3]],
                    }
                )

        structures["table_lineups"] = {
            "count": len(table_lineups),
            "samples": table_lineups[:2],
        }

        # 3. Listen-basierte Aufstellungen
        player_lists = soup.find_all("ul") + soup.find_all("ol")
        list_lineups = []
        for ul in player_lists:
            items = ul.find_all("li")
            if len(items) >= 8:  # Mindestens 8 Spieler
                list_lineups.append(
                    {
                        "item_count": len(items),
                        "sample_items": [
                            item.get_text(strip=True) for item in items[:5]
                        ],
                    }
                )

        structures["list_lineups"] = {
            "count": len(list_lineups),
            "samples": list_lineups[:2],
        }

        # 4. Div-basierte Strukturen
        all_divs = soup.find_all("div")
        potential_lineup_divs = []
        for div in all_divs:
            text = div.get_text(strip=True)
            if any(
                keyword in text.lower()
                for keyword in ["aufstellung", "lineup", "starting"]
            ):
                children = div.find_all(["div", "span", "p"])
                if len(children) >= 8:
                    potential_lineup_divs.append(
                        {
                            "children_count": len(children),
                            "div_classes": div.get("class", []),
                            "sample_texts": [
                                child.get_text(strip=True) for child in children[:5]
                            ],
                        }
                    )

        structures["div_lineups"] = {
            "count": len(potential_lineup_divs),
            "samples": potential_lineup_divs[:2],
        }

        return structures

    def analyze_goal_structures(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analysiert verschiedene Torschützen-Strukturen"""
        structures = {}

        # 1. Moderne kick__goals Struktur
        goal_elements = soup.find_all(
            class_=lambda x: x and "kick__goals" in x if x else False
        )
        structures["kick__goals"] = {"count": len(goal_elements), "samples": []}

        for goal_elem in goal_elements[:3]:
            goal_players = goal_elem.find_all(
                class_=lambda x: x and "player" in x if x else False
            )
            structures["kick__goals"]["samples"].append(
                {
                    "goal_player_count": len(goal_players),
                    "goal_texts": [gp.get_text(strip=True) for gp in goal_players],
                    "goal_classes": [gp.get("class", []) for gp in goal_players],
                }
            )

        # 2. Timeline-basierte Tore
        timeline_elements = soup.find_all(
            class_=lambda x: x and "timeline" in x if x else False
        )
        timeline_goals = []
        for timeline in timeline_elements:
            goal_items = timeline.find_all(
                lambda tag: "tor" in tag.get_text().lower()
                or "goal" in tag.get_text().lower()
            )
            if goal_items:
                timeline_goals.append(
                    {
                        "goal_count": len(goal_items),
                        "sample_goals": [
                            item.get_text(strip=True) for item in goal_items[:3]
                        ],
                    }
                )

        structures["timeline_goals"] = {
            "count": len(timeline_goals),
            "samples": timeline_goals[:2],
        }

        # 3. Tabellen mit Toren
        goal_tables = []
        for table in soup.find_all("table"):
            text = table.get_text().lower()
            if "tor" in text or "goal" in text or "minute" in text:
                rows = table.find_all("tr")
                goal_tables.append(
                    {
                        "row_count": len(rows),
                        "sample_content": table.get_text(strip=True)[:200],
                    }
                )

        structures["table_goals"] = {
            "count": len(goal_tables),
            "samples": goal_tables[:2],
        }

        # 4. Einfache Text-Suche nach Torschützen
        all_text = soup.get_text()
        goal_indicators = ["Tor:", "Goal:", "Torschütze:", "Scorer:"]
        text_goals = []
        for indicator in goal_indicators:
            if indicator in all_text:
                # Finde Kontext um den Indikator
                index = all_text.find(indicator)
                context = all_text[max(0, index - 50) : index + 100]
                text_goals.append({"indicator": indicator, "context": context.strip()})

        structures["text_goals"] = {"count": len(text_goals), "samples": text_goals[:3]}

        return structures

    def extract_html_samples(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrahiert HTML-Samples für manuelle Inspektion"""
        samples = {}

        # Sample von potentiellen Aufstellungs-Bereichen
        lineup_section = soup.find(
            string=lambda text: text and "aufstellung" in text.lower()
        )
        if lineup_section:
            parent = lineup_section.parent
            for _ in range(3):  # 3 Ebenen nach oben
                if parent and parent.parent:
                    parent = parent.parent
            if parent:
                samples["lineup_html"] = str(parent)[:1000]

        # Sample von potentiellen Tor-Bereichen
        goal_section = soup.find(
            string=lambda text: text
            and any(word in text.lower() for word in ["tor", "goal"])
        )
        if goal_section:
            parent = goal_section.parent
            for _ in range(2):  # 2 Ebenen nach oben
                if parent and parent.parent:
                    parent = parent.parent
            if parent:
                samples["goal_html"] = str(parent)[:1000]

        return samples

    async def run_analysis(self):
        """Führt die komplette Analyse durch"""
        await self.setup_client()

        print("Starte Analyse zufälliger Spiele von 1963-2025...")

        seasons = await self.get_random_seasons()
        print(f"Ausgewählte Saisons: {seasons}")

        all_results = []

        for season in seasons:
            print(f"\n=== Analysiere Saison {season} ===")

            game_urls = await self.get_random_games_from_season(season, max_games=2)

            for game_url in game_urls:
                analysis = await self.analyze_game_schema(game_url)
                if analysis:
                    analysis["season"] = season
                    all_results.append(analysis)

                # Pause zwischen Requests
                await asyncio.sleep(2)

            # Längere Pause zwischen Saisons
            await asyncio.sleep(3)

        await self.client.aclose()

        # Ergebnisse speichern
        output_file = Path("test/random_games_structure_analysis.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print(f"\nAnalyse abgeschlossen! Ergebnisse gespeichert in: {output_file}")

        # Zusammenfassung erstellen
        self.create_summary(all_results)

    def create_summary(self, results: List[Dict[str, Any]]):
        """Erstellt eine Zusammenfassung der Analyseergebnisse"""
        summary = {
            "total_games_analyzed": len(results),
            "seasons_covered": list(set([r.get("season", "Unknown") for r in results])),
            "lineup_patterns": {},
            "goal_patterns": {},
            "recommendations": [],
        }

        # Aufstellungs-Patterns aggregieren
        lineup_methods = [
            "kick__lineup__team",
            "table_lineups",
            "list_lineups",
            "div_lineups",
        ]
        for method in lineup_methods:
            counts = []
            player_counts = []

            for result in results:
                lineup_data = result.get("lineup_structures", {}).get(method, {})
                count = lineup_data.get("count", 0)
                counts.append(count)

                # Spieleranzahl aus Samples extrahieren
                samples = lineup_data.get("samples", [])
                for sample in samples:
                    if "player_count" in sample:
                        player_counts.append(sample["player_count"])
                    elif "item_count" in sample:
                        player_counts.append(sample["item_count"])

            summary["lineup_patterns"][method] = {
                "games_with_pattern": len([c for c in counts if c > 0]),
                "avg_elements": sum(counts) / len(counts) if counts else 0,
                "player_counts": player_counts,
                "avg_players": (
                    sum(player_counts) / len(player_counts) if player_counts else 0
                ),
            }

        # Tor-Patterns aggregieren
        goal_methods = ["kick__goals", "timeline_goals", "table_goals", "text_goals"]
        for method in goal_methods:
            counts = []

            for result in results:
                goal_data = result.get("goal_structures", {}).get(method, {})
                count = goal_data.get("count", 0)
                counts.append(count)

            summary["goal_patterns"][method] = {
                "games_with_pattern": len([c for c in counts if c > 0]),
                "avg_elements": sum(counts) / len(counts) if counts else 0,
            }

        # Empfehlungen basierend auf den Daten
        # Bester Aufstellungs-Selector
        best_lineup = max(
            summary["lineup_patterns"].items(), key=lambda x: x[1]["games_with_pattern"]
        )
        summary["recommendations"].append(
            f"Primärer Aufstellungs-Selector: {best_lineup[0]} (in {best_lineup[1]['games_with_pattern']} Spielen gefunden)"
        )

        # Bester Tor-Selector
        best_goals = max(
            summary["goal_patterns"].items(), key=lambda x: x[1]["games_with_pattern"]
        )
        summary["recommendations"].append(
            f"Primärer Tor-Selector: {best_goals[0]} (in {best_goals[1]['games_with_pattern']} Spielen gefunden)"
        )

        # Redundanz-Empfehlungen
        reliable_lineup_methods = [
            method
            for method, data in summary["lineup_patterns"].items()
            if data["games_with_pattern"] >= len(results) * 0.3
        ]
        summary["recommendations"].append(
            f"Redundante Aufstellungs-Methoden: {reliable_lineup_methods}"
        )

        reliable_goal_methods = [
            method
            for method, data in summary["goal_patterns"].items()
            if data["games_with_pattern"] >= len(results) * 0.3
        ]
        summary["recommendations"].append(
            f"Redundante Tor-Methoden: {reliable_goal_methods}"
        )

        # Zusammenfassung speichern
        summary_file = Path("test/structure_analysis_summary.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"Zusammenfassung gespeichert in: {summary_file}")

        # Konsolen-Output
        print("\n=== ANALYSE-ZUSAMMENFASSUNG ===")
        print(f"Analysierte Spiele: {summary['total_games_analyzed']}")
        print(f"Abgedeckte Saisons: {summary['seasons_covered']}")
        print("\nAufstellungs-Patterns:")
        for method, data in summary["lineup_patterns"].items():
            print(
                f"  {method}: {data['games_with_pattern']}/{len(results)} Spiele, ∅{data['avg_players']:.1f} Spieler"
            )
        print("\nTor-Patterns:")
        for method, data in summary["goal_patterns"].items():
            print(f"  {method}: {data['games_with_pattern']}/{len(results)} Spiele")
        print("\nEmpfehlungen:")
        for rec in summary["recommendations"]:
            print(f"  • {rec}")


async def main():
    analyzer = RandomGameStructureAnalyzer()
    await analyzer.run_analysis()


if __name__ == "__main__":
    asyncio.run(main())
