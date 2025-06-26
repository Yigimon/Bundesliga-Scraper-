import streamlit as st
import asyncio
import pandas as pd
from typing import List, Optional
import os
import sys
import time
from datetime import datetime, date
import logging
from pathlib import Path

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Import local modules
try:
    from models.game_data import GameData
    from scrapers.kicker_scraper import KickerScraper
    from exporters.excel_exporter_new import ExcelExporter
    from exporters.merge_service import MergeService
except ImportError as e:
    st.error(f"Import-Fehler: {e}")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class App:
    """Hauptanwendung mit Streamlit GUI."""

    def __init__(
        self,
        scraper: KickerScraper,
        exporter: ExcelExporter,
        merger: MergeService,
    ):
        self.scraper = scraper
        self.exporter = exporter
        self.merger = merger
        self.games_data: List[GameData] = []

    def run(self):
        """Startet die Streamlit-Anwendung."""
        st.set_page_config(
            page_title="Bundesliga Scraper",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Custom CSS für modernes Design
        st.markdown(
            """
        <style>
        .main {
            padding-top: 2rem;
        }
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            font-weight: 600;
        }
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .stSelectbox > div > div {
            border-radius: 8px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Header
        st.title("⚽ Bundesliga Scraper")
        st.markdown("*Exportiere Bundesliga-Spiele mit Torschützen und Aufstellungen*")

        # Sidebar Navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Seite auswählen",
            ["🏠 Dashboard", "📊 Batch Download", "➕ Einzelspiele", "📈 Statistiken"],
        )

        if page == "🏠 Dashboard":
            self._render_dashboard()
        elif page == "📊 Batch Download":
            self._render_batch_download()
        elif page == "➕ Einzelspiele":
            self._render_single_games()
        elif page == "📈 Statistiken":
            self._render_statistics()

    def _render_dashboard(self):
        """Rendert das Haupt-Dashboard."""
        st.header("Dashboard")

        # Filter-Sidebar
        st.sidebar.header("🔍 Filter")

        # Saison-Filter
        seasons = self._get_available_seasons()
        selected_season = st.sidebar.selectbox("Saison", ["Alle"] + seasons, index=0)

        # Team-Filter
        teams = self._get_available_teams()
        selected_team = st.sidebar.selectbox("Verein", ["Alle"] + teams, index=0)

        # Datum-Filter
        st.sidebar.subheader("Datum-Range")
        date_from = st.sidebar.date_input("Von", value=date(1963, 8, 1))
        date_to = st.sidebar.date_input("Bis", value=date.today())

        # Tore-Filter
        st.sidebar.subheader("Tore-Range")
        min_goals = st.sidebar.number_input("Mindest-Tore", min_value=0, value=0)
        max_goals = st.sidebar.number_input("Maximal-Tore", min_value=0, value=20)

        # Torschützen-Filter
        scorer_filter = st.sidebar.text_input("Torschütze (Name)")

        # Statistik-Kacheln
        if self.games_data:
            filtered_games = self._apply_filters(
                self.games_data,
                selected_season,
                selected_team,
                date_from,
                date_to,
                min_goals,
                max_goals,
                scorer_filter,
            )
            self._render_statistics_cards(filtered_games)

            # Spiele-Tabelle
            st.subheader("📋 Gefilterte Spiele")
            if filtered_games:
                df = pd.DataFrame([game.to_dict() for game in filtered_games])
                st.dataframe(df, use_container_width=True)

                # Export-Button
                if st.button("📁 Gefilterte Daten exportieren"):
                    try:
                        filename = f"filtered_games_{len(filtered_games)}.xlsx"
                        filepath = self.exporter.export_by_team(
                            filtered_games, filename
                        )
                        st.success(f"✅ Export erfolgreich: {filepath}")

                        # Download-Button
                        with open(filepath, "rb") as file:
                            st.download_button(
                                label="📥 Datei herunterladen",
                                data=file.read(),
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )
                    except Exception as e:
                        st.error(f"❌ Export-Fehler: {e}")
            else:
                st.info(
                    "Keine Spiele gefunden. Passen Sie die Filter an oder laden Sie Daten."
                )
        else:
            st.info(
                "📂 Keine Daten geladen. Verwenden Sie 'Batch Download' oder 'Einzelspiele'."
            )

    def _render_batch_download(self):
        """Rendert die Batch-Download Seite."""
        st.header("📊 Batch Download")
        st.markdown("Lade alle Spiele einer oder mehrerer Saisons automatisch.")

        # Saison-Auswahl
        col1, col2 = st.columns(2)

        with col1:
            start_year = st.number_input(
                "Start-Jahr", min_value=1963, max_value=2024, value=2023
            )

        with col2:
            end_year = st.number_input(
                "End-Jahr", min_value=1963, max_value=2024, value=2023
            )

        # Saisons generieren
        seasons = []
        for year in range(start_year, end_year + 1):
            seasons.append(f"{year}-{str(year + 1)[-2:]}")

        st.write(f"📅 Ausgewählte Saisons: {', '.join(seasons)}")

        # Download-Optionen
        st.subheader("⚙️ Optionen")
        merge_existing = st.checkbox(
            "Mit existierenden Daten zusammenführen", value=True
        )
        existing_file = None

        if merge_existing:
            uploaded_file = st.file_uploader(
                "Existierende Excel-Datei hochladen",
                type=["xlsx", "xls"],
                help="Optional: Vorhandene Daten für Zusammenführung",
            )
            if uploaded_file:
                existing_file = uploaded_file

        # Download starten
        if st.button("🚀 Batch Download starten"):
            if seasons:
                self._run_batch_download(seasons, existing_file)
            else:
                st.error("❌ Keine Saisons ausgewählt.")

    def _render_single_games(self):
        """Rendert die Einzelspiele-Seite."""
        st.header("➕ Einzelspiele hinzufügen")
        st.markdown("Fügen Sie einzelne Spiele über URLs oder CSV-Import hinzu.")

        # URL-Input
        st.subheader("🔗 URLs eingeben")
        urls_text = st.text_area(
            "Spiel-URLs (eine pro Zeile)",
            placeholder="https://www.kicker.de/muenchen-gegen-braunschweig-1963-bundesliga-20087/schema",
            height=150,
        )

        # CSV-Upload
        st.subheader("📄 CSV-Import")
        csv_file = st.file_uploader(
            "CSV-Datei mit URLs hochladen",
            type=["csv"],
            help="CSV mit einer 'url' Spalte",
        )

        # Einzelspiele verarbeiten
        if st.button("🔄 Spiele importieren"):
            urls = []

            # URLs aus Textfeld
            if urls_text.strip():
                urls.extend(
                    [url.strip() for url in urls_text.split("\n") if url.strip()]
                )

            # URLs aus CSV
            if csv_file:
                try:
                    csv_df = pd.read_csv(csv_file)
                    if "url" in csv_df.columns:
                        urls.extend(csv_df["url"].dropna().tolist())
                    else:
                        st.error("❌ CSV-Datei muss eine 'url' Spalte enthalten.")
                        return
                except Exception as e:
                    st.error(f"❌ CSV-Fehler: {e}")
                    return

            if urls:
                self._process_single_games(urls)
            else:
                st.warning("⚠️ Keine URLs gefunden.")

    def _render_statistics(self):
        """Rendert die Statistiken-Seite."""
        st.header("📈 Statistiken")

        if not self.games_data:
            st.info("📂 Keine Daten für Statistiken verfügbar. Laden Sie zuerst Daten.")
            return

        # Detaillierte Statistiken
        stats = self._calculate_detailed_statistics(self.games_data)

        # Allgemeine Statistiken
        st.subheader("📊 Allgemeine Statistiken")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Gesamte Spiele", stats["total_games"])
        with col2:
            st.metric("Gesamte Tore", stats["total_goals"])
        with col3:
            st.metric("⌀ Tore/Spiel", f"{stats['avg_goals']:.2f}")
        with col4:
            st.metric("Saisons", stats["seasons_count"])

        # Top-Listen
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Meiste Siege")
            if stats["team_wins"]:
                wins_df = pd.DataFrame(
                    list(stats["team_wins"].items()), columns=["Team", "Siege"]
                )
                st.dataframe(wins_df.head(10), use_container_width=True)

        with col2:
            st.subheader("👟 Top Torschützen")
            if stats["top_scorers"]:
                scorers_df = pd.DataFrame(
                    list(stats["top_scorers"].items()), columns=["Spieler", "Tore"]
                )
                st.dataframe(scorers_df.head(10), use_container_width=True)

        # Torreichstes Spiel
        st.subheader("🎯 Torreichstes Spiel")
        if stats["highest_scoring"]:
            game = stats["highest_scoring"]
            st.info(
                f"**{game.home_team.name} {game.home_score}:{game.away_score} {game.away_team.name}** "
                f"({game.date}) - {game.get_total_goals()} Tore"
            )

    def _run_batch_download(self, seasons: List[str], existing_file=None):
        """Führt den Batch-Download mit detaillierter Fortschrittsanzeige aus."""
        # Fortschritts-Container
        progress_container = st.container()

        with progress_container:
            col1, col2 = st.columns(2)

            with col1:
                # Download-Counter
                counter_placeholder = st.empty()
                counter_placeholder.metric(
                    "Download-Fortschritt", "0/0 Spiele", "Initialisiere..."
                )

            with col2:
                # Zeit-Schätzung
                time_placeholder = st.empty()
                time_placeholder.metric("Geschätzte Zeit", "--:--", "Berechnung...")

            # Hauptfortschrittsbalken
            progress_bar = st.progress(0)

            # Status und Geschwindigkeit
            status_placeholder = st.empty()
            speed_placeholder = st.empty()

        try:
            start_time = time.time()
            status_placeholder.text("🔄 Download gestartet...")

            # Async download ausführen
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                total_games = 0
                downloaded_games = 0

                # Für jede Saison einzeln verarbeiten für bessere Fortschrittsanzeige
                all_games = []

                for season_idx, season in enumerate(seasons, 1):
                    status_placeholder.text(
                        f"📡 Ermittle Spiele für Saison {season}..."
                    )

                    # Anzahl Spiele für diese Saison ermitteln
                    season_urls = loop.run_until_complete(
                        self.scraper.get_season_game_urls(season)
                    )

                    season_total = len(season_urls)
                    total_games += season_total

                    status_placeholder.text(
                        f"📊 Saison {season}: {season_total} Spiele gefunden"
                    )

                    # Spiele für diese Saison herunterladen
                    for game_idx, (url, expected_matchday) in enumerate(season_urls, 1):
                        downloaded_games += 1

                        # Fortschritt berechnen
                        overall_progress = (
                            (downloaded_games / total_games) * 80
                            if total_games > 0
                            else 0
                        )
                        progress_bar.progress(overall_progress / 100)

                        # Zeit-Schätzung
                        elapsed = time.time() - start_time
                        if downloaded_games > 0:
                            estimated_total = (elapsed / downloaded_games) * total_games
                            remaining = estimated_total - elapsed
                            remaining_str = (
                                f"{int(remaining//60):02d}:{int(remaining%60):02d}"
                            )

                            # Geschwindigkeit
                            speed = (downloaded_games / elapsed) * 60  # pro Minute

                            # UI Updates
                            counter_placeholder.metric(
                                "Download-Fortschritt",
                                f"{downloaded_games}/{total_games} Spiele",
                                f"Saison {season} - Spiel {game_idx}/{season_total}",
                            )

                            time_placeholder.metric(
                                "Verbleibende Zeit",
                                remaining_str,
                                f"{speed:.1f} Spiele/min",
                            )

                        # Spiel-Details anzeigen
                        game_name = url.split("/")[-2] if "/" in url else "Unbekannt"
                        status_placeholder.text(
                            f"📡 Lade Spiel {downloaded_games}/{total_games}: {game_name}"
                        )

                        # Einzelnes Spiel laden
                        game_data = loop.run_until_complete(
                            self.scraper.parse_game_detail(url)
                        )

                        if game_data:
                            if not game_data.matchday:
                                game_data.matchday = expected_matchday
                            all_games.append(game_data)

                            # Erfolg anzeigen
                            total_goals = game_data.home_score + game_data.away_score
                            speed_placeholder.success(
                                f"✅ {game_data.home_team.name} {game_data.home_score}:{game_data.away_score} {game_data.away_team.name} ({total_goals} {'Tor' if total_goals == 1 else 'Tore'})"
                            )
                        else:
                            speed_placeholder.error(
                                f"❌ Fehler beim Laden von {game_name}"
                            )

                        # Rate limiting
                        loop.run_until_complete(asyncio.sleep(1))

                progress_bar.progress(85)
                status_placeholder.text(
                    f"✅ {len(all_games)} Spiele geladen - Exportiere..."
                )

                # Mit existierenden Daten zusammenführen
                if existing_file and all_games:
                    progress_bar.progress(87)
                    status_placeholder.text(
                        "🔄 Zusammenführen mit existierenden Daten..."
                    )

                    # Existierende Datei temporär speichern
                    temp_path = f"temp_{existing_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(existing_file.read())

                    # Merge mit existierenden Daten
                    merge_success = self.merger.merge_gamedata_with_existing(
                        all_games, temp_path
                    )
                    if merge_success:
                        st.info("✅ Daten mit existierender Datei zusammengeführt")
                    else:
                        st.warning("⚠️ Merge-Vorgang mit Warnungen abgeschlossen")

                    os.remove(temp_path)  # Temp-Datei löschen

                progress_bar.progress(90)
                status_placeholder.text("📊 Exportiere nach Excel...")

                # Exportieren
                if all_games:
                    filename = f"bundesliga_batch_{len(all_games)}_spiele.xlsx"
                    filepath = self.exporter.export_by_team(all_games, filename)

                    # Finale Statistiken
                    total_time = time.time() - start_time
                    final_speed = (len(all_games) / total_time) * 60

                    progress_bar.progress(100)
                    status_placeholder.text("✅ Download und Export abgeschlossen!")

                    # Erfolgsmeldung mit Details
                    st.success(
                        f"🎉 **{len(all_games)} Spiele erfolgreich exportiert!**\n\n"
                        f"📁 **Datei:** {filename}\n"
                        f"📍 **Pfad:** {filepath}\n"
                        f"⏱️ **Dauer:** {total_time:.1f} Sekunden\n"
                        f"🚀 **Durchschnittliche Geschwindigkeit:** {final_speed:.1f} Spiele/min"
                    )

                    # Finale Statistiken anzeigen
                    counter_placeholder.metric(
                        "Download abgeschlossen",
                        f"{len(all_games)} Spiele",
                        f"✅ Alle Saisons verarbeitet",
                    )

                    time_placeholder.metric(
                        "Gesamtdauer",
                        f"{int(total_time//60):02d}:{int(total_time%60):02d}",
                        f"{final_speed:.1f} Spiele/min",
                    )

                    # Daten für Dashboard speichern
                    self.games_data = all_games

                    # Download-Button
                    with open(filepath, "rb") as file:
                        st.download_button(
                            label="📥 Excel-Datei herunterladen",
                            data=file.read(),
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                else:
                    st.warning("⚠️ Keine Spiele gefunden.")

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Batch-Download Fehler: {e}")
            st.error(f"❌ **Fehler beim Batch-Download:** {e}")
            progress_bar.progress(0)
            status_placeholder.text("❌ Download fehlgeschlagen")

            # Fehler-Details anzeigen
            counter_placeholder.metric(
                "Download-Status", "Fehlgeschlagen", "❌ Fehler aufgetreten"
            )
            time_placeholder.metric(
                "Fehlerzeit", datetime.now().strftime("%H:%M:%S"), "Retry empfohlen"
            )

    def _process_single_games(self, urls: List[str]):
        """Verarbeitet einzelne Spiel-URLs."""
        progress_bar = st.progress(0)
        status_text = st.empty()

        games = []

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:

                async def process_urls():
                    async with self.scraper:
                        for i, url in enumerate(urls):
                            status_text.text(f"🔄 Verarbeite Spiel {i+1}/{len(urls)}")

                            game = await self.scraper.parse_game_detail(url)
                            if game:
                                games.append(game)

                            progress_bar.progress((i + 1) / len(urls))

                loop.run_until_complete(process_urls())

            finally:
                loop.close()

            if games:
                # Exportieren
                filename = f"einzelspiele_{len(games)}.xlsx"
                filepath = self.exporter.export_by_team(games, filename)

                st.success(f"✅ {len(games)} Spiele erfolgreich importiert: {filepath}")

                # Zu vorhandenen Daten hinzufügen
                self.games_data.extend(games)

                # Download-Button
                with open(filepath, "rb") as file:
                    st.download_button(
                        label="📥 Excel-Datei herunterladen",
                        data=file.read(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            else:
                st.warning("⚠️ Keine gültigen Spiele aus den URLs extrahiert.")

        except Exception as e:
            logger.error(f"Einzelspiele Fehler: {e}")
            st.error(f"❌ Fehler beim Verarbeiten: {e}")

    def _apply_filters(
        self,
        games: List[GameData],
        season: str,
        team: str,
        date_from: date,
        date_to: date,
        min_goals: int,
        max_goals: int,
        scorer: str,
    ) -> List[GameData]:
        """Wendet Filter auf die Spiele-Liste an."""
        filtered = games.copy()

        # Saison-Filter
        if season != "Alle":
            filtered = [g for g in filtered if g.season == season]

        # Team-Filter
        if team != "Alle":
            filtered = [g for g in filtered if g.involves_team(team)]

        # Tore-Filter
        filtered = [
            g for g in filtered if min_goals <= g.get_total_goals() <= max_goals
        ]

        # Torschützen-Filter
        if scorer.strip():
            scorer_lower = scorer.lower()
            filtered = [
                g
                for g in filtered
                if any(
                    scorer_lower in goal.scorer.lower()
                    for goal in g.home_goals + g.away_goals
                )
            ]

        return filtered

    def _render_statistics_cards(self, games: List[GameData]):
        """Rendert Statistik-Kacheln."""
        if not games:
            return

        st.subheader("📊 Schnell-Statistiken")

        col1, col2, col3, col4 = st.columns(4)

        total_goals = sum(game.get_total_goals() for game in games)
        avg_goals = total_goals / len(games) if games else 0

        # Torreichstes Spiel
        highest_game = max(games, key=lambda g: g.get_total_goals())

        # Meiste Siege
        team_wins = {}
        for game in games:
            winner = game.get_winner()
            if winner:
                team_wins[winner] = team_wins.get(winner, 0) + 1

        top_team = (
            max(team_wins.items(), key=lambda x: x[1]) if team_wins else ("Keine", 0)
        )

        with col1:
            st.metric("🎯 Spiele", len(games))

        with col2:
            st.metric("⚽ Gesamt-Tore", total_goals)

        with col3:
            st.metric("📈 ⌀ Tore/Spiel", f"{avg_goals:.1f}")

        with col4:
            st.metric("🏆 Meiste Siege", f"{top_team[0]} ({top_team[1]})")

    def _get_available_seasons(self) -> List[str]:
        """Gibt verfügbare Saisons zurück."""
        if not self.games_data:
            return []
        return sorted(list(set(game.season for game in self.games_data if game.season)))

    def _get_available_teams(self) -> List[str]:
        """Gibt verfügbare Teams zurück."""
        if not self.games_data:
            return []
        teams = set()
        for game in self.games_data:
            teams.add(game.home_team.name)
            teams.add(game.away_team.name)
        return sorted(list(teams))

    def _calculate_detailed_statistics(self, games: List[GameData]) -> dict:
        """Berechnet detaillierte Statistiken."""
        if not games:
            return {}

        total_goals = sum(game.get_total_goals() for game in games)
        seasons = set(game.season for game in games if game.season)

        # Team-Siege
        team_wins = {}
        for game in games:
            winner = game.get_winner()
            if winner:
                team_wins[winner] = team_wins.get(winner, 0) + 1

        # Torschützen
        scorers = {}
        for game in games:
            for goal in game.home_goals + game.away_goals:
                scorers[goal.scorer] = scorers.get(goal.scorer, 0) + 1

        # Torreichstes Spiel
        highest_scoring = (
            max(games, key=lambda g: g.get_total_goals()) if games else None
        )

        return {
            "total_games": len(games),
            "total_goals": total_goals,
            "avg_goals": total_goals / len(games),
            "seasons_count": len(seasons),
            "team_wins": dict(
                sorted(team_wins.items(), key=lambda x: x[1], reverse=True)
            ),
            "top_scorers": dict(
                sorted(scorers.items(), key=lambda x: x[1], reverse=True)
            ),
            "highest_scoring": highest_scoring,
        }


def main():
    """Haupteinstiegspunkt für die Streamlit-Anwendung."""
    try:
        # Import der Konfiguration
        from config.speed_config import get_rate_limit_delay

        # Erstelle Instanzen der benötigten Services
        scraper = KickerScraper(rate_limit_delay=get_rate_limit_delay())
        exporter = ExcelExporter()
        merger = MergeService()

        # Erstelle und starte die App
        app = App(scraper=scraper, exporter=exporter, merger=merger)
        app.run()

    except Exception as e:
        st.error(f"Fehler beim Starten der Anwendung: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()
