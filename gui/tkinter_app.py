"""
Bundesliga Scraper Pro - Tkinter Desktop GUI
Moderne Desktop-Anwendung mit allen Funktionen der Streamlit-Version
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import threading
from datetime import date, datetime
from typing import List, Optional
import pandas as pd
import os
from pathlib import Path
import time

# Versuche ttkbootstrap für modernen Look zu importieren
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *

    MODERN_THEME = True
except ImportError:
    # Fallback auf normales ttk
    from tkinter import ttk

    MODERN_THEME = False

# Import der bestehenden Module (keine Änderungen!)
from models.game_data import GameData
from scrapers.kicker_scraper import KickerScraper
from exporters.excel_exporter_new import ExcelExporter
from exporters.merge_service import MergeService
from config.speed_config import get_rate_limit_delay


class TkinterApp:
    """Desktop-GUI mit Tkinter für den Bundesliga Scraper"""

    def __init__(
        self, scraper: KickerScraper, exporter: ExcelExporter, merger: MergeService
    ):
        self.scraper = scraper
        self.exporter = exporter
        self.merger = merger
        self.games_data: List[GameData] = []

        # Fortschritts-Tracking
        self.download_start_time = None
        self.games_downloaded = 0
        self.total_games = 0

        # Tkinter Setup mit modernem Theme
        if MODERN_THEME:
            # ttkbootstrap - Moderne Themes
            self.root = ttk.Window(themename="superhero")  # Dunkles, modernes Theme
        else:
            # Fallback Standard Tkinter
            self.root = tk.Tk()

        self.root.title("⚽ Bundesliga Scraper Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)

        # App Icon setzen (falls vorhanden)
        try:
            icon_path = Path("assets/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass

        # Style konfigurieren
        if not MODERN_THEME:
            self.style = ttk.Style()
            self.style.theme_use("clam")

            # Erweiterte Style-Konfiguration für modernen Look
            self.style.configure(
                "Modern.TButton",
                font=("Segoe UI", 10),
                borderwidth=0,
                focuscolor="none",
                relief="flat",
            )

            self.style.configure(
                "Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#2E3440"
            )

            self.style.configure(
                "Subtitle.TLabel", font=("Segoe UI", 11), foreground="#4C566A"
            )

        # Variablen für Filter
        self.selected_season = tk.StringVar(value="Alle")
        self.selected_team = tk.StringVar(value="Alle")
        self.min_goals = tk.IntVar(value=0)
        self.max_goals = tk.IntVar(value=20)
        self.scorer_filter = tk.StringVar()

        # GUI erstellen
        self._setup_gui()

    def _setup_gui(self):
        """Erstellt die komplette GUI-Struktur"""
        # Hauptframe
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(
            header_frame, text="⚽ Bundesliga Scraper Pro", font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(
            header_frame,
            text="Exportiere Bundesliga-Spiele mit Torschützen und Aufstellungen",
            font=("Arial", 10),
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

        # Notebook für Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs erstellen
        self._create_dashboard_tab()
        self._create_batch_download_tab()
        self._create_single_games_tab()
        self._create_statistics_tab()

    def _create_dashboard_tab(self):
        """Dashboard-Tab erstellen"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")

        # Paned Window für Filter-Sidebar und Hauptbereich
        paned = ttk.PanedWindow(dashboard_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Filter-Sidebar
        filter_frame = ttk.LabelFrame(paned, text="🔍 Filter", padding=10)
        paned.add(filter_frame, weight=1)

        # Saison-Filter
        ttk.Label(filter_frame, text="Saison:").pack(anchor=tk.W, pady=(0, 5))
        seasons = self._get_available_seasons()
        season_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.selected_season,
            values=["Alle"] + seasons,
            state="readonly",
        )
        season_combo.pack(fill=tk.X, pady=(0, 10))

        # Team-Filter
        ttk.Label(filter_frame, text="Verein:").pack(anchor=tk.W, pady=(0, 5))
        teams = self._get_available_teams()
        team_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.selected_team,
            values=["Alle"] + teams,
            state="readonly",
        )
        team_combo.pack(fill=tk.X, pady=(0, 10))

        # Tore-Filter
        ttk.Label(filter_frame, text="Tore-Range:").pack(anchor=tk.W, pady=(10, 5))

        goals_frame = ttk.Frame(filter_frame)
        goals_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(goals_frame, text="Min:").pack(side=tk.LEFT)
        min_goals_spin = ttk.Spinbox(
            goals_frame, from_=0, to=50, textvariable=self.min_goals, width=5
        )
        min_goals_spin.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(goals_frame, text="Max:").pack(side=tk.LEFT)
        max_goals_spin = ttk.Spinbox(
            goals_frame, from_=0, to=50, textvariable=self.max_goals, width=5
        )
        max_goals_spin.pack(side=tk.LEFT, padx=(5, 0))

        # Torschützen-Filter
        ttk.Label(filter_frame, text="Torschütze:").pack(anchor=tk.W, pady=(10, 5))
        scorer_entry = ttk.Entry(filter_frame, textvariable=self.scorer_filter)
        scorer_entry.pack(fill=tk.X, pady=(0, 10))

        # Filter anwenden Button
        filter_btn = ttk.Button(
            filter_frame, text="Filter anwenden", command=self._apply_dashboard_filters
        )
        filter_btn.pack(fill=tk.X, pady=(10, 0))

        # Hauptbereich für Statistiken und Spiele
        main_content = ttk.Frame(paned)
        paned.add(main_content, weight=3)

        # Statistik-Kacheln
        stats_frame = ttk.LabelFrame(main_content, text="📊 Statistiken", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.stats_labels = {}
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        # Spiele-Tabelle
        table_frame = ttk.LabelFrame(main_content, text="📋 Spiele", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview für Spiele-Tabelle
        columns = ("Datum", "Heim", "Gast", "Ergebnis", "Torschützen")
        self.games_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.games_tree.heading(col, text=col)
            self.games_tree.column(col, width=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.games_tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.HORIZONTAL, command=self.games_tree.xview
        )
        self.games_tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Pack Treeview und Scrollbars
        self.games_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_batch_download_tab(self):
        """Batch Download Tab erstellen"""
        batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(batch_frame, text="📊 Batch Download")

        # Header
        header = ttk.Label(
            batch_frame,
            text="Batch Download - Alle Spiele einer Saison",
            font=("Arial", 14, "bold"),
        )
        header.pack(pady=20)

        # Saison-Auswahl
        season_frame = ttk.Frame(batch_frame)
        season_frame.pack(pady=10)

        ttk.Label(season_frame, text="Saison auswählen:").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.batch_season_var = tk.StringVar()
        seasons = self._get_available_seasons()
        batch_season_combo = ttk.Combobox(
            season_frame,
            textvariable=self.batch_season_var,
            values=seasons,
            state="readonly",
            width=15,
        )
        batch_season_combo.pack(side=tk.LEFT)

        # Download Button
        button_frame = ttk.Frame(batch_frame)
        button_frame.pack(pady=20)

        download_btn = ttk.Button(
            button_frame,
            text="🔄 Alle Spiele herunterladen",
            command=self._start_batch_download,
        )
        download_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Exports-Ordner öffnen Button
        exports_btn = ttk.Button(
            button_frame, text="📁 Exports öffnen", command=self._open_exports_folder
        )
        exports_btn.pack(side=tk.LEFT)

        # Progress Bar und Statistiken
        progress_frame = ttk.LabelFrame(
            batch_frame, text="📊 Download-Fortschritt", padding=15
        )
        progress_frame.pack(fill=tk.X, padx=20, pady=10)

        # Fortschritts-Statistiken Zeile
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # Download-Counter
        self.download_counter_label = ttk.Label(
            stats_frame,
            text="0/0 Spiele heruntergeladen",
            font=("Segoe UI", 11, "bold"),
        )
        self.download_counter_label.pack(side=tk.LEFT)

        # Geschätzte Zeit
        self.time_estimate_label = ttk.Label(
            stats_frame,
            text="Geschätzte Zeit: --:--",
            font=("Segoe UI", 10),
            foreground="#666666",
        )
        self.time_estimate_label.pack(side=tk.RIGHT)

        # Hauptfortschrittsbalken
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode="determinate",
        )

        # Styling für Progress Bar (falls ttkbootstrap verfügbar)
        if MODERN_THEME:
            self.progress_bar.configure(bootstyle="success-striped")

        self.progress_bar.pack(fill=tk.X, pady=(5, 10))

        # Prozent-Anzeige
        self.progress_percent_label = ttk.Label(
            progress_frame, text="0%", font=("Segoe UI", 10, "bold")
        )
        self.progress_percent_label.pack()

        # Download-Geschwindigkeit
        self.speed_label = ttk.Label(
            progress_frame,
            text="Download-Geschwindigkeit: -- Spiele/min",
            font=("Segoe UI", 9),
            foreground="#888888",
        )
        self.speed_label.pack(pady=(5, 0))

        # Status Label
        self.status_label = ttk.Label(batch_frame, text="Bereit zum Download")
        self.status_label.pack(pady=10)

        # Log-Textfeld
        log_frame = ttk.LabelFrame(batch_frame, text="Download-Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.log_text = tk.Text(log_frame, height=10)
        log_scroll = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_single_games_tab(self):
        """Einzelspiele Tab erstellen"""
        single_frame = ttk.Frame(self.notebook)
        self.notebook.add(single_frame, text="➕ Einzelspiele")

        # Header
        header = ttk.Label(
            single_frame, text="Einzelspiele hinzufügen", font=("Arial", 14, "bold")
        )
        header.pack(pady=20)

        # URL-Eingabe
        url_frame = ttk.LabelFrame(single_frame, text="Spiel-URLs eingeben", padding=10)
        url_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(url_frame, text="URLs (eine pro Zeile):").pack(
            anchor=tk.W, pady=(0, 5)
        )

        self.url_text = tk.Text(url_frame, height=8)
        url_scroll = ttk.Scrollbar(
            url_frame, orient=tk.VERTICAL, command=self.url_text.yview
        )
        self.url_text.configure(yscrollcommand=url_scroll.set)

        self.url_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        url_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(single_frame)
        button_frame.pack(pady=20)

        load_btn = ttk.Button(
            button_frame, text="📥 URLs laden", command=self._load_single_games
        )
        load_btn.pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Leeren",
            command=lambda: self.url_text.delete(1.0, tk.END),
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Exports-Ordner öffnen Button
        exports_btn = ttk.Button(
            button_frame, text="📁 Exports öffnen", command=self._open_exports_folder
        )
        exports_btn.pack(side=tk.LEFT)

    def _create_statistics_tab(self):
        """Statistiken Tab erstellen"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 Statistiken")

        # Header
        header = ttk.Label(
            stats_frame, text="Detaillierte Statistiken", font=("Arial", 14, "bold")
        )
        header.pack(pady=20)

        # Placeholder für Statistiken
        placeholder = ttk.Label(
            stats_frame,
            text="Statistiken werden hier angezeigt, sobald Daten geladen sind.",
            font=("Arial", 10),
        )
        placeholder.pack(pady=50)

    def _get_available_seasons(self) -> List[str]:
        """Verfügbare Saisons zurückgeben"""
        # Standardmäßig alle Bundesliga-Saisons seit 1963
        seasons = []
        current_year = datetime.now().year
        for year in range(1963, current_year + 1):
            seasons.append(f"{year}-{str(year + 1)[2:]}")
        return seasons[::-1]  # Neueste zuerst

    def _get_available_teams(self) -> List[str]:
        """Verfügbare Teams zurückgeben"""
        # Standard Bundesliga-Teams
        return [
            "Bayern München",
            "Borussia Dortmund",
            "RB Leipzig",
            "Bayer Leverkusen",
            "Borussia Mönchengladbach",
            "Wolfsburg",
            "Eintracht Frankfurt",
            "SC Freiburg",
            "1. FC Köln",
            "VfB Stuttgart",
            "1. FSV Mainz 05",
            "TSG Hoffenheim",
            "FC Augsburg",
            "Hertha BSC",
            "Arminia Bielefeld",
            "VfL Bochum",
            "SpVgg Greuther Fürth",
            "1. FC Union Berlin",
        ]

    def _apply_dashboard_filters(self):
        """Filter auf Dashboard anwenden"""
        # Placeholder - hier würden die Filter angewendet
        self.log("Filter angewendet")

    def _start_batch_download(self):
        """Batch Download starten"""
        season = self.batch_season_var.get()
        if not season:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Saison aus.")
            return

        # Download in separatem Thread starten
        thread = threading.Thread(target=self._run_batch_download, args=(season,))
        thread.daemon = True
        thread.start()

    def _run_batch_download(self, season: str):
        """Batch Download ausführen - ECHTE IMPLEMENTIERUNG mit detailliertem Fortschritt"""
        try:
            # Download-Tracking initialisieren
            self.download_start_time = time.time()
            self.games_downloaded = 0
            self.total_games = 0

            self.log(f"🔄 Starte Download für Saison {season}...")
            self.status_label.config(text=f"Download läuft für {season}...")
            self._update_progress_display(0, 0, "Initialisiere...")

            # Async download in eigenem Event Loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Zuerst: Anzahl der Spiele ermitteln
                self.log(f"📡 Ermittle Spielanzahl für Saison {season}...")
                season_urls = loop.run_until_complete(
                    self.scraper.get_season_game_urls(season)
                )

                self.total_games = len(season_urls)
                self.log(f"📊 {self.total_games} Spiele gefunden")
                self._update_progress_display(
                    0, self.total_games, "Download startet..."
                )

                # Echten Download starten mit Progress-Tracking
                games = []

                for i, (url, expected_matchday) in enumerate(season_urls, 1):
                    self.games_downloaded = i

                    # Progress und Zeit-Schätzung aktualisieren
                    self._update_progress_display(
                        i, self.total_games, f"Lade Spiel {i}"
                    )

                    self.log(
                        f"📡 Spiel {i}/{self.total_games}: {url.split('/')[-2] if '/' in url else 'Unbekannt'}"
                    )

                    # Einzelnes Spiel laden
                    game_data = loop.run_until_complete(
                        self.scraper.parse_game_detail(url)
                    )

                    if game_data:
                        if not game_data.matchday:
                            game_data.matchday = expected_matchday
                        games.append(game_data)

                        total_goals = game_data.home_score + game_data.away_score
                        self.log(
                            f"✅ {game_data.home_team.name} {game_data.home_score}:{game_data.away_score} {game_data.away_team.name} ({total_goals} {'Tor' if total_goals == 1 else 'Tore'})"
                        )
                    else:
                        self.log(f"❌ Fehler beim Laden")

                    # Rate limiting
                    loop.run_until_complete(asyncio.sleep(1))

                # Download abgeschlossen
                self._update_progress_display(
                    self.total_games, self.total_games, "Download abgeschlossen"
                )
                self.log(f"✅ Alle {len(games)} Spiele geladen")

                if games:
                    # Excel Export
                    self.log("📊 Exportiere nach Excel...")
                    self._update_progress_display(
                        self.total_games, self.total_games, "Exportiere nach Excel..."
                    )

                    filename = f"bundesliga_batch_{len(games)}_spiele.xlsx"

                    # Export - ExcelExporter kümmert sich um den exports Ordner
                    export_path = self.exporter.export_by_team(games, filename)

                    self.log(f"🎉 Excel-Datei erstellt: {export_path}")
                    self.log(
                        f"💾 Datei gespeichert unter: {Path(export_path).absolute()}"
                    )

                    # Daten für Dashboard speichern
                    self.games_data = games
                    self._update_dashboard_with_data()

                    # Finaler Status
                    total_time = time.time() - self.download_start_time
                    self.status_label.config(
                        text=f"✅ Download abgeschlossen: {len(games)} Spiele in {total_time:.1f}s"
                    )

                    # Success Dialog
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Download erfolgreich",
                            f"🎉 {len(games)} Spiele erfolgreich heruntergeladen!\n\n"
                            f"📁 Datei: {filename}\n"
                            f"📍 Pfad: {Path(export_path).absolute()}\n\n"
                            f"⏱️ Dauer: {total_time:.1f} Sekunden\n"
                            f"🚀 Geschwindigkeit: {len(games)/(total_time/60):.1f} Spiele/min\n\n"
                            f"Die Datei wurde im 'exports' Ordner gespeichert.",
                        ),
                    )

                else:
                    self.log("⚠️ Keine Spiele gefunden für diese Saison")
                    self.status_label.config(text="⚠️ Keine Spiele gefunden")
                    self._reset_progress_display()

                    self.root.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Keine Daten",
                            f"Für die Saison {season} wurden keine Spiele gefunden.\n"
                            f"Prüfen Sie die Saison-Auswahl.",
                        ),
                    )

            finally:
                loop.close()

        except Exception as e:
            error_msg = f"❌ Fehler beim Download: {str(e)}"
            self.log(error_msg)
            self.status_label.config(text="❌ Download fehlgeschlagen")
            self._reset_progress_display()

            # Error Dialog
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Download-Fehler",
                    f"Fehler beim Download der Saison {season}:\n\n{str(e)}\n\n"
                    f"Überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.",
                ),
            )

    def _update_progress_display(self, current: int, total: int, status: str = ""):
        """Aktualisiert alle Fortschrittsanzeigen"""
        if total == 0:
            progress_percent = 0
        else:
            progress_percent = (current / total) * 100

        # Progress Bar
        self.progress_var.set(progress_percent)

        # Counter
        self.download_counter_label.config(
            text=f"{current}/{total} Spiele heruntergeladen"
        )

        # Prozent
        self.progress_percent_label.config(text=f"{progress_percent:.1f}%")

        # Zeit-Schätzung
        if self.download_start_time and current > 0:
            elapsed = time.time() - self.download_start_time
            if current < total:
                estimated_total = (elapsed / current) * total
                remaining = estimated_total - elapsed
                remaining_str = f"{int(remaining//60):02d}:{int(remaining%60):02d}"
                self.time_estimate_label.config(text=f"Verbleibend: {remaining_str}")
            else:
                self.time_estimate_label.config(text=f"Abgeschlossen in {elapsed:.1f}s")

            # Download-Geschwindigkeit
            speed = (current / elapsed) * 60  # Spiele pro Minute
            self.speed_label.config(text=f"Geschwindigkeit: {speed:.1f} Spiele/min")
        else:
            self.time_estimate_label.config(text="Geschätzte Zeit: Berechnung...")
            self.speed_label.config(text="Geschwindigkeit: Berechnung...")

        # Status
        if status:
            self.status_label.config(text=status)

        # GUI aktualisieren
        self.root.update_idletasks()

    def _reset_progress_display(self):
        """Setzt alle Fortschrittsanzeigen zurück"""
        self.progress_var.set(0)
        self.download_counter_label.config(text="0/0 Spiele heruntergeladen")
        self.progress_percent_label.config(text="0%")
        self.time_estimate_label.config(text="Geschätzte Zeit: --:--")
        self.speed_label.config(text="Geschwindigkeit: -- Spiele/min")
        self.games_downloaded = 0
        self.total_games = 0
        self.download_start_time = None

    def _update_dashboard_with_data(self):
        """Dashboard mit geladenen Daten aktualisieren"""
        if not self.games_data:
            return

        # Spiele-Tabelle aktualisieren
        for item in self.games_tree.get_children():
            self.games_tree.delete(item)

        # Neue Daten einfügen
        for game in self.games_data[:100]:  # Nur erste 100 für Performance
            scorers = ", ".join(
                [f"{goal.scorer}" for goal in game.goals[:3]]
            )  # Erste 3 Torschützen
            if len(game.goals) > 3:
                scorers += "..."

            self.games_tree.insert(
                "",
                "end",
                values=(
                    game.date,
                    game.home_team.name,
                    game.away_team.name,
                    f"{game.home_score}:{game.away_score}",
                    scorers,
                ),
            )

        self.log(f"📊 Dashboard aktualisiert mit {len(self.games_data)} Spielen")

    def _load_single_games(self):
        """Einzelspiele laden - ECHTE IMPLEMENTIERUNG"""
        urls = self.url_text.get(1.0, tk.END).strip().split("\n")
        urls = [url.strip() for url in urls if url.strip()]

        if not urls:
            messagebox.showwarning(
                "Warnung", "Bitte geben Sie mindestens eine URL ein."
            )
            return

        # Download in separatem Thread starten
        thread = threading.Thread(target=self._run_single_games_download, args=(urls,))
        thread.daemon = True
        thread.start()

    def _run_single_games_download(self, urls: List[str]):
        """Einzelspiele Download ausführen"""
        try:
            self.log(f"🔄 Lade {len(urls)} Einzelspiele...")

            # Async download in eigenem Event Loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                games = []

                for i, url in enumerate(urls, 1):
                    self.log(f"📡 Spiel {i}/{len(urls)}: {url}")

                    # Einzelnes Spiel laden
                    game_data = loop.run_until_complete(
                        self.scraper.parse_game_detail(url)
                    )

                    if game_data:
                        games.append(game_data)
                        self.log(
                            f"✅ {game_data.home_team.name} {game_data.home_score}:{game_data.away_score} {game_data.away_team.name}"
                        )
                    else:
                        self.log(f"❌ Fehler beim Laden von {url}")

                    # Rate limiting
                    loop.run_until_complete(asyncio.sleep(1))

                if games:
                    # Excel Export
                    self.log("📊 Exportiere Einzelspiele nach Excel...")
                    filename = f"einzelspiele_{len(games)}.xlsx"

                    # Export - ExcelExporter kümmert sich um den exports Ordner
                    export_path = self.exporter.export_by_team(games, filename)

                    self.log(f"🎉 Excel-Datei erstellt: {export_path}")
                    self.log(
                        f"💾 Datei gespeichert unter: {Path(export_path).absolute()}"
                    )

                    # Success Dialog
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Einzelspiele erfolgreich",
                            f"🎉 {len(games)} Einzelspiele erfolgreich heruntergeladen!\n\n"
                            f"📁 Datei: {filename}\n"
                            f"📍 Pfad: {Path(export_path).absolute()}\n\n"
                            f"Die Datei wurde im 'exports' Ordner gespeichert.",
                        ),
                    )

                    # URL-Feld leeren
                    self.root.after(0, lambda: self.url_text.delete(1.0, tk.END))

                else:
                    self.log("⚠️ Keine Spiele konnten geladen werden")
                    self.root.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Keine Daten",
                            "Keine der angegebenen URLs konnte erfolgreich geladen werden.\n"
                            "Überprüfen Sie die URLs und Ihre Internetverbindung.",
                        ),
                    )

            finally:
                loop.close()

        except Exception as e:
            error_msg = f"❌ Fehler beim Laden der Einzelspiele: {str(e)}"
            self.log(error_msg)

            # Error Dialog
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Download-Fehler",
                    f"Fehler beim Laden der Einzelspiele:\n\n{str(e)}\n\n"
                    f"Überprüfen Sie die URLs und Ihre Internetverbindung.",
                ),
            )

    def _open_exports_folder(self):
        """Öffnet den Exports-Ordner im Windows Explorer"""
        try:
            exports_dir = Path("exports")
            exports_dir.mkdir(exist_ok=True)

            import subprocess
            import platform

            if platform.system() == "Windows":
                subprocess.run(["explorer", str(exports_dir.absolute())])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(exports_dir.absolute())])
            else:  # Linux
                subprocess.run(["xdg-open", str(exports_dir.absolute())])

            self.log(f"📁 Exports-Ordner geöffnet: {exports_dir.absolute()}")

        except Exception as e:
            self.log(f"❌ Fehler beim Öffnen des Exports-Ordners: {str(e)}")
            messagebox.showerror(
                "Fehler", f"Der Exports-Ordner konnte nicht geöffnet werden:\n{str(e)}"
            )

    def log(self, message: str):
        """Nachricht in Log-Bereich hinzufügen"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        if hasattr(self, "log_text"):
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)

    def run(self):
        """Anwendung starten"""
        self.root.mainloop()


if __name__ == "__main__":
    # Test der Tkinter-App
    from scrapers.kicker_scraper import KickerScraper
    from exporters.excel_exporter_new import ExcelExporter
    from exporters.merge_service import MergeService

    app = TkinterApp(
        scraper=KickerScraper(), exporter=ExcelExporter(), merger=MergeService()
    )
    app.run()
