"""
Bundesliga Scraper - Moderne Streamlit GUI (Clean Design)
"""

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


def init_page_config():
    """Initialisiert die Seiten-Konfiguration mit modernem Design."""
    st.set_page_config(
        page_title="Bundesliga Scraper Pro",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_modern_css():
    """Wendet modernes CSS-Styling an."""
    st.markdown(
        """
    <style>
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header Styles */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: white;
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        text-align: center;
    }
    
    /* Card Styles */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .card-title {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
        color: white !important;
        opacity: 1 !important;
    }
    
    .stButton > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
        color: white !important;
    }
    
    /* Success/Error Messages */
    .success-message {
        background: #10b981;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #ef4444;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #f8fafc;
    }
    
    /* Data Table */
    .dataframe {
        border: none !important;
    }
    
    .dataframe th {
        background: #f1f5f9 !important;
        color: #374151 !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    .dataframe td {
        border: none !important;
        padding: 0.75rem !important;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e0e6ed;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Remove default padding */
    .css-18e3th9 {
        padding-top: 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def show_header():
    """Zeigt den modernen Header an."""
    st.markdown(
        """
    <div class="header-container">
        <h1 class="header-title">⚽ Bundesliga Scraper Pro</h1>
        <p class="header-subtitle">Professioneller Datenexport für alle Bundesliga-Saisons seit 1963/64</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def show_stats_cards(games_data: List[GameData]):
    """Zeigt Statistik-Karten an."""
    if not games_data:
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_games = len(games_data)
        st.metric("Gesamte Spiele", total_games, help="Anzahl der geladenen Spiele")

    with col2:
        total_goals = sum(
            game.home_score + game.away_score
            for game in games_data
            if game.home_score is not None and game.away_score is not None
        )
        st.metric("Tore insgesamt", total_goals, help="Alle geschossenen Tore")

    with col3:
        seasons = len(set(game.season for game in games_data if game.season))
        st.metric("Saisons", seasons, help="Verschiedene Saisons")

    with col4:
        teams = len(
            set(
                [game.home_team for game in games_data]
                + [game.away_team for game in games_data]
            )
        )
        st.metric("Vereine", teams, help="Verschiedene Vereine")


class ModernBundesligaApp:
    """Moderne Bundesliga Scraper Anwendung."""

    def __init__(self):
        # Initialisiere Komponenten
        self.scraper = KickerScraper()
        self.exporter = ExcelExporter()
        self.exporter.output_dir = Path("exports")
        self.merger = MergeService()
        self.games_data: List[GameData] = []

        # Session State initialisieren
        if "games_data" not in st.session_state:
            st.session_state.games_data = []
        if "last_update" not in st.session_state:
            st.session_state.last_update = None
        if "export_dir" not in st.session_state:
            st.session_state.export_dir = "exports"

    def run(self):
        """Startet die Anwendung."""
        init_page_config()
        apply_modern_css()

        show_header()

        # Hauptbereich
        self.show_main_interface()

        # Footer
        st.markdown("---")
        st.markdown(
            "**Bundesliga Scraper Pro** | Entwickelt für professionelle Datenanalyse"
        )

    def show_main_interface(self):
        """Zeigt die Hauptbenutzeroberfläche."""
        # Sidebar für Navigation
        with st.sidebar:
            st.header("🔧 Funktionen")

            page = st.selectbox(
                "Wählen Sie eine Funktion:",
                [
                    "🏠 Dashboard",
                    "📊 Batch Download",
                    "➕ Einzelspiele",
                    "📈 Statistiken",
                    "⚙️ Einstellungen",
                    "📋 Lizenz & Copyright",
                ],
            )

        # Hauptinhalt basierend auf ausgewählter Seite
        if page == "🏠 Dashboard":
            self.show_dashboard()
        elif page == "📊 Batch Download":
            self.show_batch_download()
        elif page == "➕ Einzelspiele":
            self.show_single_games()
        elif page == "📈 Statistiken":
            self.show_statistics()
        elif page == "⚙️ Einstellungen":
            self.show_settings()
        elif page == "📋 Lizenz & Copyright":
            self.show_license()

    def show_dashboard(self):
        """Zeigt das Dashboard."""
        st.header("📊 Dashboard")

        # Stats Cards
        show_stats_cards(st.session_state.games_data)

        if st.session_state.games_data:
            st.subheader("🔍 Spiele-Filter")

            col1, col2, col3 = st.columns(3)

            with col1:
                seasons = sorted(
                    set(
                        game.season
                        for game in st.session_state.games_data
                        if game.season
                    )
                )
                selected_season = st.selectbox("Saison:", ["Alle"] + seasons)

            with col2:
                teams = sorted(
                    set(
                        [game.home_team for game in st.session_state.games_data]
                        + [game.away_team for game in st.session_state.games_data]
                    )
                )
                selected_team = st.selectbox("Verein:", ["Alle"] + teams)

            with col3:
                min_goals = st.number_input("Min. Tore:", min_value=0, value=0)

            # Gefilterte Daten anzeigen
            filtered_games = self.filter_games(
                st.session_state.games_data, selected_season, selected_team, min_goals
            )

            if filtered_games:
                st.subheader(f"📋 Gefilterte Spiele ({len(filtered_games)})")
                df = self.games_to_dataframe(filtered_games)
                st.dataframe(df, use_container_width=True)

                # Export Button
                if st.button("📥 Gefilterte Daten exportieren"):
                    self.export_games(filtered_games, "filtered_games")
        else:
            st.info(
                "📥 Laden Sie zunächst Spieldaten über 'Batch Download' oder 'Einzelspiele'."
            )

    def show_batch_download(self):
        """Zeigt die Batch-Download-Seite."""
        st.header("📊 Batch Download")
        st.markdown(
            "Laden Sie alle Spiele einer oder mehrerer Saisons automatisch herunter."
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            # Saison-Auswahl
            current_year = datetime.now().year
            seasons = [
                f"{year}/{str(year+1)[2:]}" for year in range(1963, current_year)
            ]

            season_option = st.radio(
                "Saison-Auswahl:",
                ["Einzelne Saison", "Mehrere Saisons", "Alle Saisons"],
            )

            selected_seasons = []
            if season_option == "Einzelne Saison":
                season = st.selectbox("Saison:", seasons)
                selected_seasons = [season]
            elif season_option == "Mehrere Saisons":
                selected_seasons = st.multiselect("Saisons:", seasons)
            else:  # Alle Saisons
                selected_seasons = seasons
                st.info(f"📅 Alle {len(seasons)} Saisons werden heruntergeladen.")

        with col2:
            st.subheader("⚙️ Download-Einstellungen")

            speed_profile = st.selectbox(
                "Geschwindigkeitsprofil:",
                ["Langsam (sicher)", "Normal", "Schnell", "Sehr schnell"],
            )

            parallel_downloads = st.checkbox("Parallele Downloads", value=True)

            if parallel_downloads:
                max_workers = st.slider("Max. parallele Downloads:", 1, 10, 3)
            else:
                max_workers = 1

        # Download starten
        if st.button("🚀 Download starten", type="primary"):
            if selected_seasons:
                self.start_batch_download(selected_seasons, speed_profile, max_workers)
            else:
                st.error("❌ Bitte wählen Sie mindestens eine Saison aus.")

    def show_single_games(self):
        """Zeigt die Einzelspiele-Seite."""
        st.header("➕ Einzelspiele hinzufügen")

        tab1, tab2 = st.tabs(["🔗 URL eingeben", "📁 Datei hochladen"])

        with tab1:
            st.markdown("Fügen Sie einzelne Spiele über kicker.de URLs hinzu:")

            urls_text = st.text_area(
                "Spiel-URLs (eine pro Zeile):",
                placeholder="https://www.kicker.de/muenchen-gegen-dortmund-2024-bundesliga-123456/schema\nhttps://www.kicker.de/...",
            )

            if st.button("🔍 URLs verarbeiten"):
                if urls_text.strip():
                    urls = [url.strip() for url in urls_text.split("\n") if url.strip()]
                    self.process_single_urls(urls)
                else:
                    st.error("❌ Bitte geben Sie mindestens eine URL ein.")

        with tab2:
            st.markdown("Laden Sie eine CSV/Excel-Datei mit URLs hoch:")

            uploaded_file = st.file_uploader(
                "Datei auswählen",
                type=["csv", "xlsx", "xls"],
                help="Die Datei sollte eine Spalte 'URL' oder 'url' enthalten.",
            )

            if uploaded_file and st.button("📊 Datei verarbeiten"):
                self.process_uploaded_file(uploaded_file)

    def show_statistics(self):
        """Zeigt detaillierte Statistiken."""
        st.header("📈 Detaillierte Statistiken")

        if not st.session_state.games_data:
            st.info("📥 Laden Sie zunächst Spieldaten.")
            return

        games = st.session_state.games_data

        # Grundstatistiken
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_games = len(games)
            st.metric("🎯 Gesamte Spiele", total_games)

        with col2:
            total_goals = sum(
                game.home_score + game.away_score
                for game in games
                if game.home_score is not None and game.away_score is not None
            )
            avg_goals = total_goals / total_games if total_games > 0 else 0
            st.metric("⚽ Durchschn. Tore/Spiel", f"{avg_goals:.2f}")

        with col3:
            high_scoring = sum(
                1
                for game in games
                if game.home_score is not None
                and game.away_score is not None
                and (game.home_score + game.away_score) >= 4
            )
            st.metric("🔥 Torspektakel (4+ Tore)", high_scoring)

        with col4:
            draws = sum(
                1
                for game in games
                if game.home_score is not None
                and game.away_score is not None
                and game.home_score == game.away_score
            )
            st.metric("🤝 Unentschieden", draws)

        # Top Teams
        st.subheader("🏆 Top Vereine")

        team_stats = {}
        for game in games:
            if game.home_score is not None and game.away_score is not None:
                # Home team
                if game.home_team not in team_stats:
                    team_stats[game.home_team] = {
                        "games": 0,
                        "wins": 0,
                        "goals_for": 0,
                        "goals_against": 0,
                    }

                team_stats[game.home_team]["games"] += 1
                team_stats[game.home_team]["goals_for"] += game.home_score
                team_stats[game.home_team]["goals_against"] += game.away_score

                if game.home_score > game.away_score:
                    team_stats[game.home_team]["wins"] += 1

                # Away team
                if game.away_team not in team_stats:
                    team_stats[game.away_team] = {
                        "games": 0,
                        "wins": 0,
                        "goals_for": 0,
                        "goals_against": 0,
                    }

                team_stats[game.away_team]["games"] += 1
                team_stats[game.away_team]["goals_for"] += game.away_score
                team_stats[game.away_team]["goals_against"] += game.home_score

                if game.away_score > game.home_score:
                    team_stats[game.away_team]["wins"] += 1

        # Top Teams DataFrame
        team_df_data = []
        for team, stats in team_stats.items():
            win_rate = (
                (stats["wins"] / stats["games"] * 100) if stats["games"] > 0 else 0
            )
            avg_goals = (
                (stats["goals_for"] / stats["games"]) if stats["games"] > 0 else 0
            )

            team_df_data.append(
                {
                    "Verein": team,
                    "Spiele": stats["games"],
                    "Siege": stats["wins"],
                    "Siegquote (%)": f"{win_rate:.1f}",
                    "Tore": stats["goals_for"],
                    "Ø Tore/Spiel": f"{avg_goals:.1f}",
                }
            )

        team_df = pd.DataFrame(team_df_data)
        team_df = team_df.sort_values("Siege", ascending=False).head(10)

        st.dataframe(team_df, use_container_width=True)

    def show_settings(self):
        """Zeigt die Einstellungen."""
        st.header("⚙️ Einstellungen")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔧 Scraper-Einstellungen")

            # Request Delay
            request_delay = st.slider(
                "Request-Verzögerung (Sekunden):",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
                help="Pause zwischen den Anfragen",
            )

            # Timeout
            timeout = st.slider(
                "Request-Timeout (Sekunden):",
                min_value=5,
                max_value=60,
                value=10,
                help="Maximale Wartezeit pro Anfrage",
            )

            # Retry Attempts
            retry_attempts = st.slider(
                "Wiederholungsversuche:",
                min_value=1,
                max_value=5,
                value=3,
                help="Anzahl der Wiederholungen bei Fehlern",
            )

        with col2:
            st.subheader("📁 Export-Einstellungen")

            # Export Format
            export_format = st.selectbox(
                "Standard-Exportformat:",
                ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
                index=0,
            )

            # Include Extended Data
            include_lineups = st.checkbox("Aufstellungen einbeziehen", value=True)
            include_goalscorers = st.checkbox("Torschützen einbeziehen", value=True)
            include_cards = st.checkbox("Karten einbeziehen", value=False)

            # Output Directory
            st.markdown("**📂 Download-Pfad:**")
            current_dir = st.session_state.get("export_dir", "exports")

            col2a, col2b = st.columns([3, 1])
            with col2a:
                new_output_dir = st.text_input(
                    "Export-Verzeichnis:",
                    value=current_dir,
                    help="Ordner für die exportierten Dateien",
                    label_visibility="collapsed",
                )

            with col2b:
                if st.button("📁 Durchsuchen"):
                    # Zeige eine File-Dialog Alternative mit vorgefertigten Optionen
                    st.markdown("**📂 Häufig verwendete Pfade:**")
                    
                    # Desktop
                    desktop_path = os.path.expanduser("~/Desktop")
                    if st.button(f"�️ Desktop ({desktop_path})", key="desktop_btn"):
                        export_path = os.path.join(desktop_path, "BundesligaExports")
                        st.session_state.export_dir = export_path
                        st.rerun()
                    
                    # Documents
                    documents_path = os.path.expanduser("~/Documents")
                    if st.button(f"📄 Dokumente ({documents_path})", key="docs_btn"):
                        export_path = os.path.join(documents_path, "BundesligaExports")
                        st.session_state.export_dir = export_path
                        st.rerun()
                    
                    # Downloads
                    downloads_path = os.path.expanduser("~/Downloads")
                    if st.button(f"📥 Downloads ({downloads_path})", key="downloads_btn"):
                        export_path = os.path.join(downloads_path, "BundesligaExports")
                        st.session_state.export_dir = export_path
                        st.rerun()
                    
                    st.info("💡 Oder geben Sie den gewünschten Pfad direkt im Eingabefeld ein.")
                    
            # Prüfe ob sich der Pfad geändert hat
            if new_output_dir != current_dir:
                st.session_state.export_dir = new_output_dir

            # Zeige aktuellen Pfad an
            abs_path = os.path.abspath(new_output_dir)
            st.text(f"Vollständiger Pfad: {abs_path}")
            
            # Zeige Ordnerstatus
            if os.path.exists(new_output_dir):
                st.success(f"✅ Ordner existiert und ist bereit")
                # Zeige Anzahl vorhandener Dateien
                try:
                    files = [f for f in os.listdir(new_output_dir) if f.endswith(('.xlsx', '.csv', '.json'))]
                    if files:
                        st.info(f"📊 {len(files)} Export-Datei(en) im Ordner gefunden")
                except:
                    pass
            else:
                st.warning(f"⚠️ Ordner existiert noch nicht (wird bei Export erstellt)")

        # Einstellungen speichern
        if st.button("💾 Einstellungen speichern", type="primary"):
            # Update settings
            new_settings = {
                "request_delay": request_delay,
                "timeout": timeout,
                "retry_attempts": retry_attempts,
                "export_format": export_format,
                "include_lineups": include_lineups,
                "include_goalscorers": include_goalscorers,
                "include_cards": include_cards,
                "export_directory": new_output_dir,
            }

            # Update exporter with new directory
            self.exporter.output_dir = Path(new_output_dir)

            # Update session state
            st.session_state.export_dir = new_output_dir

            st.success("✅ Einstellungen gespeichert!")
            st.balloons()

        # Zeige Settings-Vorschau
        st.subheader("📋 Aktuelle Einstellungen")

        settings_preview = {
            "🔧 Download-Verzögerung": f"{request_delay} Sek.",
            "⏱️ Timeout": f"{timeout} Sek.",
            "🔄 Wiederholungen": f"{retry_attempts}x",
            "📄 Export-Format": export_format,
            "📂 Export-Pfad": new_output_dir,
            "📊 Include Aufstellungen": "✅" if include_lineups else "❌",
            "⚽ Include Torschützen": "✅" if include_goalscorers else "❌",
            "🟨 Include Karten": "✅" if include_cards else "❌",
        }

        for key, value in settings_preview.items():
            st.write(f"**{key}:** {value}")

        # Cache leeren
        st.subheader("🗑️ Cache & Daten")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Cache leeren"):
                if hasattr(st, "cache_data"):
                    st.cache_data.clear()
                st.success("✅ Cache geleert!")

        with col2:
            if st.button("🗑️ Session-Daten löschen"):
                for key in list(st.session_state.keys()):
                    if key not in ["settings"]:
                        del st.session_state[key]
                st.success("✅ Session-Daten gelöscht!")

        with col3:
            games_count = len(st.session_state.get("games_data", []))
            st.metric("💾 Geladene Spiele", games_count)

    def show_license(self):
        """Zeigt Lizenz & Copyright Informationen."""
        st.header("🛡️ Lizenz & Copyright")

        # Copyright Notice
        st.subheader("📜 Copyright & Eigentumsrechte")
        st.info(
            """
        **© 2025 ZeyDev - Alle Rechte vorbehalten**
        
        Diese Software ist urheberrechtlich geschützt und Eigentum von ZeyDev.
        Jede unbefugte Nutzung, Vervielfältigung oder Verbreitung ist strengstens untersagt.
        """
        )

        # License Agreement
        st.subheader("📋 Lizenzvereinbarung")

        with st.expander("📄 Vollständige Lizenzbedingungen anzeigen", expanded=False):
            st.markdown(
                """
            **LIZENZVEREINBARUNG - BUNDESLIGA SCRAPER PRO**
            
            **1. GEWÄHRTE RECHTE**  
            Diese Software wird unter einer eingeschränkten Lizenz zur Verfügung gestellt. Der Benutzer erhält das Recht zur Nutzung der Software ausschließlich für persönliche, nicht-kommerzielle Zwecke.
            
            **2. BESCHRÄNKUNGEN**
            - Kommerzielle Nutzung ist ohne ausdrückliche schriftliche Genehmigung von ZeyDev untersagt
            - Reverse Engineering, Dekompilierung oder Disassemblierung ist verboten
            - Weiterverteilung ohne Genehmigung ist nicht gestattet
            - Modifikation des Quellcodes ist nicht erlaubt
            
            **3. GEISTIGES EIGENTUM**  
            Alle Rechte, Titel und Interessen an der Software verbleiben bei ZeyDev. Dies umfasst:
            - Urheberrechte
            - Markenrechte  
            - Geschäftsgeheimnisse
            - Sonstige geistige Eigentumsrechte
            
            **4. HAFTUNGSAUSSCHLUSS**  
            Die Software wird "wie besehen" bereitgestellt. ZeyDev übernimmt keine Gewährleistung für:
            - Funktionsfähigkeit
            - Fehlerfreiheit
            - Eignung für bestimmte Zwecke
            - Verfügbarkeit von Datenquellen
            
            **5. HAFTUNGSBEGRENZUNG**  
            ZeyDev haftet nicht für Schäden, die durch die Nutzung der Software entstehen, einschließlich:
            - Datenverlust
            - Geschäftsunterbrechung
            - Entgangene Gewinne
            - Sonstige mittelbare Schäden
            
            **6. DATENSCHUTZ**  
            Die Software respektiert die Datenschutzbestimmungen der verwendeten Datenquellen. Der Benutzer ist verpflichtet:
            - Robots.txt zu beachten
            - Angemessene Request-Intervalle einzuhalten
            - Keine übermäßige Serverbelastung zu verursachen
            
            **7. BEENDIGUNG**  
            Diese Lizenz kann von ZeyDev jederzeit ohne Vorankündigung beendet werden bei:
            - Verstoß gegen die Lizenzbedingungen
            - Missbrauch der Software
            - Kommerzielle Nutzung ohne Genehmigung
            
            Bei Beendigung ist die Software vollständig zu entfernen.
            
            **Kontakt: ZeyDev**  
            Für Lizenzanfragen und kommerzielle Nutzung kontaktieren Sie ZeyDev.
            
            **Durch die Nutzung der Software erkennen Sie diese Bedingungen vollständig an.**
            """
            )

        # Software Information
        st.subheader("ℹ️ Software-Informationen")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
            **📊 Bundesliga Scraper Pro**
            - Version: 2.3
            - Entwickelt: 2025
            - Lizenztyp: Proprietär
            """
            )

        with col2:
            st.markdown(
                """
            **🛡️ ZeyDev**
            - Alle Rechte vorbehalten
            - Kommerzielle Lizenzen verfügbar
            - Professioneller Support erhältlich
            """
            )

        # Acceptance
        st.subheader("✅ Lizenzannahme")

        if st.button("📋 Ich akzeptiere die Lizenzbedingungen", type="primary"):
            st.success(
                "✅ Lizenzbedingungen akzeptiert! Vielen Dank für die Nutzung von Bundesliga Scraper Pro."
            )
            st.balloons()

        st.warning(
            "⚠️ **Wichtiger Hinweis**: Durch die Nutzung dieser Software stimmen Sie automatisch den oben genannten Lizenzbedingungen zu."
        )

    def filter_games(
        self, games: List[GameData], season: str, team: str, min_goals: int
    ) -> List[GameData]:
        """Filtert Spiele nach den angegebenen Kriterien."""
        filtered = games

        if season != "Alle":
            filtered = [game for game in filtered if game.season == season]

        if team != "Alle":
            filtered = [
                game for game in filtered if team in [game.home_team, game.away_team]
            ]

        if min_goals > 0:
            filtered = [
                game
                for game in filtered
                if game.home_score is not None
                and game.away_score is not None
                and (game.home_score + game.away_score) >= min_goals
            ]

        return filtered

    def games_to_dataframe(self, games: List[GameData]) -> pd.DataFrame:
        """Konvertiert Spieldaten zu DataFrame."""
        data = []
        for game in games:
            data.append(
                {
                    "Datum": game.date.strftime("%d.%m.%Y") if game.date else "N/A",
                    "Saison": game.season or "N/A",
                    "Heimteam": game.home_team or "N/A",
                    "Auswärtsteam": game.away_team or "N/A",
                    "Ergebnis": (
                        f"{game.home_score}:{game.away_score}"
                        if game.home_score is not None and game.away_score is not None
                        else "N/A"
                    ),
                    "Tore gesamt": (game.home_score or 0) + (game.away_score or 0),
                    "Torschützen": (
                        ", ".join(game.goalscorers) if game.goalscorers else "N/A"
                    ),
                }
            )

        return pd.DataFrame(data)

    def start_batch_download(
        self, seasons: List[str], speed_profile: str, max_workers: int
    ):
        """Startet den Batch-Download."""
        # Speed Profile Mapping
        speed_delays = {
            "Langsam (sicher)": 2.0,
            "Normal": 1.0,
            "Schnell": 0.5,
            "Sehr schnell": 0.1,
        }

        delay = speed_delays.get(speed_profile, 1.0)

        progress_bar = st.progress(0)
        status_text = st.empty()

        with st.spinner(f"🔄 Downloading {len(seasons)} Saison(en)..."):
            try:
                # Setup asyncio event loop
                import asyncio
                
                # Create scraper with appropriate delay
                scraper = KickerScraper(rate_limit_delay=delay)
                
                # Run the async batch download
                status_text.text("� Initialisiere Download...")
                # Create enhanced progress display
                progress_container = st.container()
                
                with progress_container:
                    # Progress metrics columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        games_counter = st.empty()
                        games_counter.metric("📊 Spiele", "0 / 0")
                    
                    with col2:
                        percentage_display = st.empty()
                        percentage_display.metric("📈 Fortschritt", "0%")
                    
                    with col3:
                        current_season = st.empty()
                        current_season.metric("📅 Saison", "Wird geladen...")
                    
                    with col4:
                        time_remaining = st.empty()
                        time_remaining.metric("⏱️ Verbleibend", "--:--")
                    
                    # Detailed progress info
                    progress_details = st.empty()
                
                # Progress tracking
                start_time = time.time()
                
                def update_progress(current: int, total: int, status: str = ""):
                    """Updates the Streamlit progress display."""
                    if total == 0:  # Prevent division by zero
                        return
                        
                    # Calculate progress
                    progress = current / total if total > 0 else 0
                    percentage = progress * 100
                    
                    # Update progress bar
                    progress_bar.progress(min(progress, 1.0))  # Ensure max is 1.0
                    
                    # Update metrics
                    games_counter.metric("📊 Spiele", f"{current} / {total}")
                    percentage_display.metric("📈 Fortschritt", f"{percentage:.1f}%")
                    
                    # Update status
                    status_text.text(status)
                    
                    # Calculate time estimation
                    if current > 0 and current < total:
                        elapsed_time = time.time() - start_time
                        avg_time_per_game = elapsed_time / current
                        remaining_games = total - current
                        
                        if remaining_games > 0:
                            estimated_remaining = avg_time_per_game * remaining_games
                            minutes = int(estimated_remaining // 60)
                            seconds = int(estimated_remaining % 60)
                            time_remaining.metric("⏱️ Verbleibend", f"{minutes:02d}:{seconds:02d}")
                        else:
                            time_remaining.metric("⏱️ Verbleibend", "Abgeschlossen!")
                    elif current >= total:
                        time_remaining.metric("⏱️ Verbleibend", "Abgeschlossen!")
                    
                    # Extract season from status for current season display
                    if "Saison" in status:
                        season_part = status.split("Saison ")[1].split(" -")[0] if " -" in status else "Unbekannt"
                        current_season.metric("📅 Saison", season_part)
                    elif "Analysiere" in status:
                        current_season.metric("📅 Status", "Analysiere...")
                    elif "abgeschlossen" in status.lower():
                        current_season.metric("📅 Status", "Abgeschlossen!")
                    
                    # Update detailed progress
                    progress_details.text(f"🔄 {status}")
                
                # Run with progress callback
                games = asyncio.run(scraper.batch_download_with_progress(seasons, update_progress))
                
                # Store games in session state
                st.session_state["current_games"] = games
                
                # Auto-export to Excel
                if games:
                    export_filename = f"bundesliga_batch_{len(games)}_spiele.xlsx"
                    
                    # Ensure exports directory exists
                    export_dir = st.session_state.get("export_dir", "exports")
                    os.makedirs(export_dir, exist_ok=True)
                    
                    # Use ExcelExporter
                    exporter = ExcelExporter()
                    exporter.set_output_directory(export_dir)
                    exported_file = exporter.export_by_team(games, export_filename)
                    
                    progress_bar.progress(1.0)
                    status_text.text("✅ Download abgeschlossen!")
                    
                    st.success(f"✅ {len(seasons)} Saison(en) erfolgreich heruntergeladen!")
                    st.success(f"📁 {len(games)} Spiele in {exported_file} exportiert!")
                    
                    # Download button for the exported file
                    with open(exported_file, "rb") as file:
                        st.download_button(
                            label="📥 Excel-Datei herunterladen",
                            data=file.read(),
                            file_name=os.path.basename(exported_file),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            except Exception as e:
                st.error(f"❌ Fehler beim Download: {str(e)}")

    def process_single_urls(self, urls: List[str]):
        """Verarbeitet einzelne URLs."""
        with st.spinner(f"🔄 Verarbeite {len(urls)} URL(s)..."):
            try:
                import asyncio
                
                # Create scraper
                scraper = KickerScraper()
                
                # Process URLs asynchronously
                games = []
                for url in urls:
                    if url.strip() and "kicker.de" in url:
                        game = asyncio.run(scraper.parse_game_detail(url))
                        if game:
                            games.append(game)
                
                # Store games in session state
                current_games = st.session_state.get("current_games", [])
                current_games.extend(games)
                st.session_state["current_games"] = current_games
                
                # Auto-export to Excel
                if games:
                    export_filename = f"einzelspiele_{len(games)}.xlsx"
                    
                    # Ensure exports directory exists
                    export_dir = st.session_state.get("export_dir", "exports")
                    os.makedirs(export_dir, exist_ok=True)
                    
                    # Use ExcelExporter
                    exporter = ExcelExporter()
                    exporter.set_output_directory(export_dir)
                    exported_file = exporter.export_by_team(games, export_filename)
                    
                    st.success(f"✅ {len(games)} Spiel(e) erfolgreich hinzugefügt!")
                    st.success(f"📁 Daten in {exported_file} exportiert!")
                    
                    # Download button for the exported file
                    with open(exported_file, "rb") as file:
                        st.download_button(
                            label="📥 Excel-Datei herunterladen",
                            data=file.read(),
                            file_name=os.path.basename(exported_file),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            except Exception as e:
                st.error(f"❌ Fehler bei der URL-Verarbeitung: {str(e)}")

    def process_uploaded_file(self, uploaded_file):
        """Verarbeitet eine hochgeladene Datei."""
        try:
            # Datei lesen
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # URL-Spalte finden
            url_column = None
            for col in df.columns:
                if "url" in col.lower():
                    url_column = col
                    break

            if url_column:
                urls = df[url_column].dropna().tolist()
                st.success(f"✅ {len(urls)} URLs aus Datei extrahiert!")
                self.process_single_urls(urls)
            else:
                st.error("❌ Keine URL-Spalte in der Datei gefunden.")

        except Exception as e:
            st.error(f"❌ Fehler beim Lesen der Datei: {str(e)}")

    def export_games(self, games: List[GameData], filename: str):
        """Exportiert Spiele zu Excel."""
        try:
            df = self.games_to_dataframe(games)

            # Export-Verzeichnis aus Settings holen
            export_dir = st.session_state.export_dir

            # Excel-Datei erstellen
            excel_path = os.path.join(
                export_dir,
                f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            )
            os.makedirs(export_dir, exist_ok=True)

            df.to_excel(excel_path, index=False)

            st.success(f"✅ {len(games)} Spiele exportiert nach: {excel_path}")

            # Download-Button
            with open(excel_path, "rb") as file:
                st.download_button(
                    label="📥 Datei herunterladen",
                    data=file.read(),
                    file_name=f"{filename}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        except Exception as e:
            st.error(f"❌ Exportfehler: {str(e)}")


def main():
    """Hauptfunktion."""
    app = ModernBundesligaApp()
    app.run()


if __name__ == "__main__":
    main()
