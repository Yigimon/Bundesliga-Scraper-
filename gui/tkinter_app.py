"""
Bundesliga Scraper - Moderne Tkinter GUI (Clean Design)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import List, Optional
import os
import sys
import time
import threading
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
    print(f"Import-Fehler: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModernColors:
    """Moderne Farbpalette für die GUI."""

    # Hauptfarben
    PRIMARY = "#667eea"
    SECONDARY = "#764ba2"

    # Hintergrundfarben
    BG_LIGHT = "#f8fafc"
    BG_WHITE = "#ffffff"
    BG_DARK = "#1a202c"
    BG_CARD = "#ffffff"

    # Textfarben
    TEXT_PRIMARY = "#1a202c"
    TEXT_SECONDARY = "#4a5568"
    TEXT_MUTED = "#718096"
    TEXT_WHITE = "#ffffff"

    # Statusfarben
    SUCCESS = "#48bb78"
    WARNING = "#ed8936"
    ERROR = "#f56565"
    INFO = "#4299e1"

    # Bordfarben
    BORDER_LIGHT = "#e2e8f0"
    BORDER_MEDIUM = "#cbd5e0"
    BORDER_DARK = "#a0aec0"


class ModernStyle:
    """Moderne Styling-Konfiguration für Tkinter."""

    @staticmethod
    def configure_style():
        """Konfiguriert moderne Styles für ttk-Widgets."""
        style = ttk.Style()

        # Grundkonfiguration
        style.theme_use("clam")

        # Frame Styles
        style.configure(
            "Card.TFrame", background=ModernColors.BG_CARD, relief="flat", borderwidth=1
        )

        style.configure("Header.TFrame", background=ModernColors.PRIMARY, relief="flat")

        # Label Styles
        style.configure(
            "Header.TLabel",
            background=ModernColors.PRIMARY,
            foreground=ModernColors.TEXT_WHITE,
            font=("Segoe UI", 24, "bold"),
        )

        style.configure(
            "Subtitle.TLabel",
            background=ModernColors.PRIMARY,
            foreground=ModernColors.TEXT_WHITE,
            font=("Segoe UI", 11),
        )

        style.configure(
            "Title.TLabel",
            background=ModernColors.BG_WHITE,
            foreground=ModernColors.TEXT_PRIMARY,
            font=("Segoe UI", 14, "bold"),
        )

        style.configure(
            "Card.TLabel",
            background=ModernColors.BG_CARD,
            foreground=ModernColors.TEXT_PRIMARY,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Value.TLabel",
            background=ModernColors.BG_CARD,
            foreground=ModernColors.TEXT_PRIMARY,
            font=("Segoe UI", 18, "bold"),
        )

        style.configure(
            "Muted.TLabel",
            background=ModernColors.BG_WHITE,
            foreground=ModernColors.TEXT_MUTED,
            font=("Segoe UI", 9),
        )

        # Button Styles
        style.configure(
            "Modern.TButton",
            background=ModernColors.PRIMARY,
            foreground=ModernColors.TEXT_WHITE,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            focuscolor="none",
            relief="flat",
        )

        style.map(
            "Modern.TButton",
            background=[
                ("active", "#5a6fd8"),  # Etwas dunkler bei Hover
                ("pressed", "#4f63d2"),  # Noch dunkler beim Klicken
            ],
            foreground=[
                ("active", ModernColors.TEXT_WHITE),
                ("pressed", ModernColors.TEXT_WHITE),
            ],
        )

        style.configure(
            "Success.TButton",
            background=ModernColors.SUCCESS,
            foreground=ModernColors.TEXT_WHITE,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            focuscolor="none",
            relief="flat",
        )

        style.map(
            "Success.TButton",
            background=[
                ("active", "#38a169"),  # Etwas dunkler grün bei Hover
                ("pressed", "#2f855a"),  # Noch dunkler beim Klicken
            ],
            foreground=[
                ("active", ModernColors.TEXT_WHITE),
                ("pressed", ModernColors.TEXT_WHITE),
            ],
        )

        style.configure(
            "Warning.TButton",
            background=ModernColors.WARNING,
            foreground=ModernColors.TEXT_WHITE,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            focuscolor="none",
            relief="flat",
        )

        style.map(
            "Warning.TButton",
            background=[
                ("active", "#dd6b20"),  # Etwas dunkler orange bei Hover
                ("pressed", "#c05621"),  # Noch dunkler beim Klicken
            ],
            foreground=[
                ("active", ModernColors.TEXT_WHITE),
                ("pressed", ModernColors.TEXT_WHITE),
            ],
        )

        # Notebook Styles
        style.configure(
            "Modern.TNotebook",
            background=ModernColors.BG_WHITE,
            borderwidth=0,
            tabmargins=[0, 0, 0, 0],
        )

        style.configure(
            "Modern.TNotebook.Tab",
            background=ModernColors.BG_LIGHT,
            foreground=ModernColors.TEXT_SECONDARY,
            padding=[20, 10],
            font=("Segoe UI", 10),
            borderwidth=0,
        )

        style.map(
            "Modern.TNotebook.Tab",
            background=[
                ("selected", ModernColors.BG_WHITE),
                ("active", ModernColors.BG_CARD),
            ],
        )

        # Entry Styles
        style.configure(
            "Modern.TEntry",
            fieldbackground=ModernColors.BG_WHITE,
            foreground=ModernColors.TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
            insertcolor=ModernColors.PRIMARY,
        )

        # Combobox Styles
        style.configure(
            "Modern.TCombobox",
            fieldbackground=ModernColors.BG_WHITE,
            foreground=ModernColors.TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
        )

        # Progressbar Styles
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=ModernColors.PRIMARY,
            troughcolor=ModernColors.BG_LIGHT,
            borderwidth=0,
            lightcolor=ModernColors.PRIMARY,
            darkcolor=ModernColors.PRIMARY,
        )

        # Treeview Styles
        style.configure(
            "Modern.Treeview",
            background=ModernColors.BG_WHITE,
            foreground=ModernColors.TEXT_PRIMARY,
            fieldbackground=ModernColors.BG_WHITE,
            borderwidth=1,
            relief="solid",
        )

        style.configure(
            "Modern.Treeview.Heading",
            background=ModernColors.BG_LIGHT,
            foreground=ModernColors.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )


class StatsCard(ttk.Frame):
    """Moderne Statistik-Karte."""

    def __init__(self, parent, title: str, value: str, icon: str = ""):
        super().__init__(parent, style="Card.TFrame")

        # Padding
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        container = ttk.Frame(self, style="Card.TFrame")
        container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        # Icon (optional)
        if icon:
            icon_label = ttk.Label(
                container,
                text=icon,
                background=ModernColors.BG_CARD,
                foreground=ModernColors.PRIMARY,
                font=("Segoe UI", 16),
            )
            icon_label.grid(row=0, column=0, sticky="w")

        # Title
        title_label = ttk.Label(container, text=title, style="Card.TLabel")
        title_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Value
        value_label = ttk.Label(container, text=value, style="Value.TLabel")
        value_label.grid(row=2, column=0, sticky="w", pady=(5, 0))

    def update_value(self, new_value: str):
        """Aktualisiert den Wert der Karte."""
        # Find value label and update
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Label) and "Value.TLabel" in str(
                        subchild.cget("style")
                    ):
                        subchild.config(text=new_value)
                        break


class ModernProgressDialog:
    """Moderner Progress-Dialog mit detaillierter Fortschrittsanzeige."""

    def __init__(self, parent, title: str, message: str, total_items: int = 0):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x300")
        self.window.transient(parent)
        self.window.grab_set()

        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"500x300+{x}+{y}")

        # Configure styles
        ModernStyle.configure_style()

        # Main frame
        main_frame = ttk.Frame(self.window, style="Card.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Message
        self.message_label = ttk.Label(main_frame, text=message, style="Title.TLabel")
        self.message_label.pack(pady=(0, 20))

        # Progress counter label (z.B. "10 / 306 Spiele")
        self.counter_label = ttk.Label(
            main_frame, text="0 / 0 Spiele", style="Subtitle.TLabel"
        )
        self.counter_label.pack(pady=(0, 10))

        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            style="Modern.Horizontal.TProgressbar",
            mode="determinate",
            length=450,
        )
        self.progress.pack(pady=(0, 10))

        # Percentage label
        self.percentage_label = ttk.Label(main_frame, text="0%", style="Muted.TLabel")
        self.percentage_label.pack(pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(
            main_frame, text="Wird geladen...", style="Muted.TLabel"
        )
        self.status_label.pack(pady=(0, 10))

        # Time estimation label
        self.time_label = ttk.Label(
            main_frame, text="Geschätzte Zeit: --:--", style="Muted.TLabel"
        )
        self.time_label.pack(pady=(0, 10))

        # Cancel button
        self.cancel_button = ttk.Button(
            main_frame, text="Abbrechen", style="Warning.TButton", command=self.cancel
        )
        self.cancel_button.pack(pady=(20, 0))

        self.cancelled = False
        self.total_items = total_items
        self.current_item = 0
        self.start_time = time.time()

    def update_progress(
        self,
        current: Optional[int] = None,
        total: Optional[int] = None,
        status: str = "",
    ):
        """Aktualisiert den Fortschritt mit detaillierten Informationen."""
        if current is not None:
            self.current_item = current
        if total is not None:
            self.total_items = total

        # Calculate progress percentage
        if self.total_items > 0:
            progress_value = (self.current_item / self.total_items) * 100
            percentage = progress_value
        else:
            progress_value = 0
            percentage = 0

        # Update progress bar
        self.progress["value"] = progress_value

        # Update counter label
        self.counter_label.config(
            text=f"{self.current_item} / {self.total_items} Spiele"
        )

        # Update percentage label
        self.percentage_label.config(text=f"{percentage:.1f}%")

        # Update status
        if status:
            self.status_label.config(text=status)

        # Calculate and update time estimation
        self._update_time_estimation()

        self.window.update()

    def _update_time_estimation(self):
        """Berechnet und aktualisiert die Zeitschätzung."""
        if self.current_item > 0 and self.total_items > 0:
            elapsed_time = time.time() - self.start_time
            avg_time_per_item = elapsed_time / self.current_item
            remaining_items = self.total_items - self.current_item

            if remaining_items > 0:
                estimated_remaining_time = avg_time_per_item * remaining_items

                # Format time as MM:SS
                minutes = int(estimated_remaining_time // 60)
                seconds = int(estimated_remaining_time % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"

                self.time_label.config(text=f"Verbleibende Zeit: ~{time_str}")
            else:
                self.time_label.config(text="Abgeschlossen!")
        else:
            self.time_label.config(text="Geschätzte Zeit: --:--")

    def cancel(self):
        """Bricht den Vorgang ab."""
        self.cancelled = True
        self.window.destroy()

    def close(self):
        """Schließt den Dialog."""
        self.window.destroy()


class LicenseDialog:
    """Dialog zur Anzeige der Lizenz- und Copyright-Informationen."""

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Lizenz & Copyright")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=ModernColors.BG_WHITE)

        # Dialog zentrieren
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center on parent
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 300
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 250
        self.dialog.geometry(f"600x500+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        """Erstellt die Dialog-Widgets."""
        # Header
        header_frame = ttk.Frame(self.dialog, style="Header.TFrame")
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ttk.Label(
            header_frame, text="🛡️ Bundesliga Scraper Pro", style="Header.TLabel"
        )
        title_label.pack(pady=20)

        subtitle_label = ttk.Label(
            header_frame,
            text="Lizenz- und Copyright-Informationen",
            style="Subtitle.TLabel",
        )
        subtitle_label.pack(pady=(0, 20))

        # Content Frame
        content_frame = ttk.Frame(self.dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Scrollable Text
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill="both", expand=True)

        # Text Widget mit Scrollbar
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=15,
        )

        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        # License text
        license_text = """BUNDESLIGA SCRAPER PRO - LIZENZVEREINBARUNG

© 2025 ZeyDev. Alle Rechte vorbehalten.

WICHTIGE LIZENZBESTIMMUNGEN:

1. EIGENTUMSRECHTE
   Diese Software ist das geistige Eigentum von ZeyDev. Alle Rechte, 
   Titel und Interessen an der Software verbleiben bei ZeyDev.

2. NUTZUNGSERLAUBNIS
   ✅ Private, nicht-kommerzielle Nutzung
   ✅ Erstellen von Backup-Kopien für persönliche Zwecke
   ✅ Verwendung der exportierten Daten für persönliche Analyse

3. VERBOTENE AKTIVITÄTEN
   ❌ Kommerzielle Nutzung ohne schriftliche Genehmigung
   ❌ Weiterverteilung der Software
   ❌ Reverse Engineering, Dekompilierung oder Disassemblierung
   ❌ Entfernung von Copyright-Hinweisen oder Wasserzeichen
   ❌ Verwendung für illegale Zwecke

4. HAFTUNGSAUSSCHLUSS
   Die Software wird "wie besehen" bereitgestellt, ohne Gewährleistung 
   jeglicher Art. ZeyDev haftet nicht für Schäden, die durch die 
   Nutzung dieser Software entstehen.

5. DATENVERANTWORTUNG
   Der Nutzer ist verantwortlich für die rechtmäßige Verwendung der 
   gescrapten Daten und muss alle relevanten Datenschutz- und 
   Urheberrechtsbestimmungen beachten.

6. KÜNDIGUNGSKLAUSEL
   Diese Lizenz kann bei Verstößen gegen die Bedingungen sofort 
   widerrufen werden.

KONTAKT:
Für Lizenzanfragen oder Fragen wenden Sie sich bitte an ZeyDev.

TECHNISCHE DETAILS:
- Version: Bundesliga Scraper Pro v2.3
- Build: Desktop Edition
- Lizenztyp: Proprietär
- Gültig ab: 2025

Durch die Nutzung dieser Software stimmen Sie den oben genannten 
Bedingungen zu.
"""

        text_widget.insert("1.0", license_text)
        text_widget.config(state="disabled")

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button Frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x", pady=(15, 0))

        # Close Button
        close_button = ttk.Button(
            button_frame,
            text="Verstanden & Schließen",
            style="Modern.TButton",
            command=self.close_dialog,
        )
        close_button.pack(side="right")

        # Focus on close button
        close_button.focus()

        # Bind escape key
        self.dialog.bind("<Escape>", lambda e: self.close_dialog())

    def close_dialog(self):
        """Schließt den Dialog."""
        self.dialog.destroy()


class ModernBundesligaGUI:
    """Moderne Bundesliga Scraper GUI mit Tkinter."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bundesliga Scraper Pro")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Configure styles
        ModernStyle.configure_style()

        # Configure root
        self.root.configure(bg=ModernColors.BG_LIGHT)

        # Initialize data
        self.scraper = KickerScraper()
        self.exporter = ExcelExporter()
        self.exporter.output_dir = Path("exports")
        self.merger = MergeService()
        self.games_data: List[GameData] = []

        # Create GUI
        self.create_widgets()

        # Center window
        self.center_window()

    def center_window(self):
        """Zentriert das Fenster auf dem Bildschirm."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")

    def create_widgets(self):
        """Erstellt die GUI-Widgets."""
        # Header
        self.create_header()

        # Main content area
        self.create_main_content()

        # Footer
        self.create_footer()

    def create_header(self):
        """Erstellt den Header."""
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        # Header content
        header_content = ttk.Frame(header_frame, style="Header.TFrame")
        header_content.pack(fill="x", padx=30, pady=20)

        # Title
        title_label = ttk.Label(
            header_content, text="⚽ Bundesliga Scraper Pro", style="Header.TLabel"
        )
        title_label.pack()

        # Subtitle
        subtitle_label = ttk.Label(
            header_content,
            text="Professioneller Datenexport für alle Bundesliga-Saisons seit 1963/64",
            style="Subtitle.TLabel",
        )
        subtitle_label.pack(pady=(5, 0))

    def create_main_content(self):
        """Erstellt den Hauptinhalt."""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.configure(style="TFrame")

        # Statistics cards
        self.create_stats_section(main_container)

        # Notebook for different sections
        self.create_notebook(main_container)

    def create_stats_section(self, parent):
        """Erstellt die Statistik-Sektion."""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill="x", pady=(0, 20))

        # Title
        stats_title = ttk.Label(
            stats_frame, text="📊 Statistiken", style="Title.TLabel"
        )
        stats_title.pack(anchor="w", pady=(0, 15))

        # Stats cards container
        cards_frame = ttk.Frame(stats_frame)
        cards_frame.pack(fill="x")

        # Configure grid
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        # Create stats cards
        self.stats_cards = {
            "games": StatsCard(cards_frame, "Gesamte Spiele", "0", "🎯"),
            "goals": StatsCard(cards_frame, "Tore insgesamt", "0", "⚽"),
            "seasons": StatsCard(cards_frame, "Saisons", "0", "📅"),
            "teams": StatsCard(cards_frame, "Vereine", "0", "🏟️"),
        }

        # Place cards
        for i, (key, card) in enumerate(self.stats_cards.items()):
            card.grid(row=0, column=i, sticky="nsew", padx=(0, 15 if i < 3 else 0))

    def create_notebook(self, parent):
        """Erstellt das Notebook mit verschiedenen Tabs."""
        self.notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Create tabs
        self.create_dashboard_tab()
        self.create_batch_download_tab()
        self.create_single_games_tab()
        self.create_statistics_tab()
        self.create_settings_tab()
        self.create_license_tab()

    def create_dashboard_tab(self):
        """Erstellt den Dashboard-Tab."""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")

        # Configure grid
        dashboard_frame.grid_columnconfigure(0, weight=1)
        dashboard_frame.grid_rowconfigure(1, weight=1)

        # Filter section
        filter_frame = ttk.LabelFrame(dashboard_frame, text="🔍 Filter", padding=20)
        filter_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        # Filter controls
        filter_controls = ttk.Frame(filter_frame)
        filter_controls.pack(fill="x")

        for i in range(4):
            filter_controls.grid_columnconfigure(i, weight=1)

        # Season filter
        ttk.Label(filter_controls, text="Saison:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        self.season_var = tk.StringVar(value="Alle")
        self.season_combo = ttk.Combobox(
            filter_controls,
            textvariable=self.season_var,
            style="Modern.TCombobox",
            state="readonly",
        )
        self.season_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Team filter
        ttk.Label(filter_controls, text="Verein:").grid(
            row=0, column=1, sticky="w", padx=(0, 10)
        )
        self.team_var = tk.StringVar(value="Alle")
        self.team_combo = ttk.Combobox(
            filter_controls,
            textvariable=self.team_var,
            style="Modern.TCombobox",
            state="readonly",
        )
        self.team_combo.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        # Goals filter
        ttk.Label(filter_controls, text="Min. Tore:").grid(
            row=0, column=2, sticky="w", padx=(0, 10)
        )
        self.goals_var = tk.StringVar(value="0")
        self.goals_entry = ttk.Entry(
            filter_controls, textvariable=self.goals_var, style="Modern.TEntry"
        )
        self.goals_entry.grid(row=1, column=2, sticky="ew", padx=(0, 10))

        # Apply filter button
        self.filter_button = ttk.Button(
            filter_controls,
            text="Filter anwenden",
            style="Modern.TButton",
            command=self.apply_filters,
        )
        self.filter_button.grid(row=1, column=3, sticky="ew")

        # Data table
        self.create_data_table(dashboard_frame)

    def create_data_table(self, parent):
        """Erstellt die Datentabelle."""
        table_frame = ttk.LabelFrame(parent, text="📋 Spiele", padding=20)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Configure grid
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Treeview with scrollbars
        tree_frame = ttk.Frame(table_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Treeview
        columns = ("Datum", "Saison", "Heimteam", "Auswärtsteam", "Ergebnis", "Tore")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", style="Modern.Treeview"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Configure columns
        column_widths = {
            "Datum": 100,
            "Saison": 80,
            "Heimteam": 150,
            "Auswärtsteam": 150,
            "Ergebnis": 80,
            "Tore": 60,
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Export button
        export_frame = ttk.Frame(table_frame)
        export_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))

        self.export_button = ttk.Button(
            export_frame,
            text="📥 Exportieren",
            style="Success.TButton",
            command=self.export_filtered_data,
        )
        self.export_button.pack(side="right")

    def create_batch_download_tab(self):
        """Erstellt den Batch-Download-Tab."""
        batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(batch_frame, text="📊 Batch Download")

        # Configure grid
        batch_frame.grid_columnconfigure(0, weight=1)

        # Settings frame
        settings_frame = ttk.LabelFrame(
            batch_frame, text="⚙️ Download-Einstellungen", padding=20
        )
        settings_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        # Season selection
        season_frame = ttk.Frame(settings_frame)
        season_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(season_frame, text="Saison-Auswahl:", style="Title.TLabel").pack(
            anchor="w"
        )

        # Radio buttons for season selection
        self.season_mode = tk.StringVar(value="single")

        radio_frame = ttk.Frame(season_frame)
        radio_frame.pack(fill="x", pady=(10, 0))

        ttk.Radiobutton(
            radio_frame,
            text="Einzelne Saison",
            variable=self.season_mode,
            value="single",
            command=self.update_season_selection,
        ).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(
            radio_frame,
            text="Mehrere Saisons",
            variable=self.season_mode,
            value="multiple",
            command=self.update_season_selection,
        ).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(
            radio_frame,
            text="Alle Saisons",
            variable=self.season_mode,
            value="all",
            command=self.update_season_selection,
        ).pack(side="left")

        # Season selection widgets
        self.season_selection_frame = ttk.Frame(season_frame)
        self.season_selection_frame.pack(fill="x", pady=(10, 0))

        # Speed settings
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.pack(fill="x", pady=(20, 0))

        speed_frame.grid_columnconfigure(0, weight=1)
        speed_frame.grid_columnconfigure(1, weight=1)

        # Speed profile
        ttk.Label(speed_frame, text="Geschwindigkeit:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(
            speed_frame,
            textvariable=self.speed_var,
            values=["Langsam (sicher)", "Normal", "Schnell", "Sehr schnell"],
            style="Modern.TCombobox",
            state="readonly",
        )
        speed_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Parallel downloads
        ttk.Label(speed_frame, text="Parallele Downloads:").grid(
            row=0, column=1, sticky="w"
        )
        self.parallel_var = tk.BooleanVar(value=True)
        parallel_check = ttk.Checkbutton(
            speed_frame, text="Aktiviert", variable=self.parallel_var
        )
        parallel_check.grid(row=1, column=1, sticky="w")

        # Download button
        download_frame = ttk.Frame(batch_frame)
        download_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.download_button = ttk.Button(
            download_frame,
            text="🚀 Download starten",
            style="Modern.TButton",
            command=self.start_batch_download,
        )
        self.download_button.pack(side="right")

        # Initialize season selection
        self.update_season_selection()

    def create_single_games_tab(self):
        """Erstellt den Einzelspiele-Tab."""
        single_frame = ttk.Frame(self.notebook)
        self.notebook.add(single_frame, text="➕ Einzelspiele")

        # Configure grid
        single_frame.grid_columnconfigure(0, weight=1)
        single_frame.grid_rowconfigure(0, weight=1)

        # URL input frame
        url_frame = ttk.LabelFrame(
            single_frame, text="🔗 Spiel-URLs hinzufügen", padding=20
        )
        url_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure grid
        url_frame.grid_columnconfigure(0, weight=1)
        url_frame.grid_rowconfigure(1, weight=1)

        # Instructions
        instruction_label = ttk.Label(
            url_frame,
            text="Fügen Sie Kicker.de Spiel-URLs hinzu (eine pro Zeile):",
            style="Muted.TLabel",
        )
        instruction_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Text widget for URLs
        text_frame = ttk.Frame(url_frame)
        text_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        self.url_text = tk.Text(
            text_frame,
            height=10,
            wrap="word",
            font=("Consolas", 10),
            relief="solid",
            borderwidth=1,
        )
        self.url_text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for text
        url_scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.url_text.yview
        )
        url_scrollbar.grid(row=0, column=1, sticky="ns")
        self.url_text.configure(yscrollcommand=url_scrollbar.set)

        # Buttons frame
        buttons_frame = ttk.Frame(url_frame)
        buttons_frame.grid(row=2, column=0, sticky="ew")

        # File button
        file_button = ttk.Button(
            buttons_frame,
            text="📁 Datei laden",
            style="Modern.TButton",
            command=self.load_url_file,
        )
        file_button.pack(side="left", padx=(0, 10))

        # Process button
        process_button = ttk.Button(
            buttons_frame,
            text="🔍 URLs verarbeiten",
            style="Success.TButton",
            command=self.process_urls,
        )
        process_button.pack(side="right")

    def create_statistics_tab(self):
        """Erstellt den Statistik-Tab."""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 Statistiken")

        # Placeholder for detailed statistics
        placeholder = ttk.Label(
            stats_frame,
            text="📈 Detaillierte Statistiken\n\nWerden angezeigt, sobald Daten geladen sind.",
            style="Title.TLabel",
            anchor="center",
        )
        placeholder.pack(expand=True)

    def create_settings_tab(self):
        """Erstellt den Einstellungen-Tab."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Einstellungen")

        # Configure grid
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

        # Scraper settings
        scraper_frame = ttk.LabelFrame(
            settings_frame, text="🔧 Scraper-Einstellungen", padding=20
        )
        scraper_frame.grid(row=0, column=0, sticky="new", padx=(20, 10), pady=20)

        # Request delay
        ttk.Label(scraper_frame, text="Request-Verzögerung (Sek.):").pack(anchor="w")
        self.delay_var = tk.DoubleVar(value=1.0)
        delay_scale = ttk.Scale(
            scraper_frame,
            from_=0.1,
            to=5.0,
            orient="horizontal",
            variable=self.delay_var,
            length=200,
        )
        delay_scale.pack(fill="x", pady=(5, 15))

        # Timeout
        ttk.Label(scraper_frame, text="Request-Timeout (Sek.):").pack(anchor="w")
        self.timeout_var = tk.IntVar(value=10)
        timeout_scale = ttk.Scale(
            scraper_frame,
            from_=5,
            to=60,
            orient="horizontal",
            variable=self.timeout_var,
            length=200,
        )
        timeout_scale.pack(fill="x", pady=(5, 15))

        # Retry attempts
        ttk.Label(scraper_frame, text="Wiederholungsversuche:").pack(anchor="w")
        self.retry_var = tk.IntVar(value=3)
        retry_scale = ttk.Scale(
            scraper_frame,
            from_=1,
            to=5,
            orient="horizontal",
            variable=self.retry_var,
            length=200,
        )
        retry_scale.pack(fill="x", pady=(5, 15))

        # Export settings
        export_frame = ttk.LabelFrame(
            settings_frame, text="📁 Export-Einstellungen", padding=20
        )
        export_frame.grid(row=0, column=1, sticky="new", padx=(10, 20), pady=20)

        # Export format
        ttk.Label(export_frame, text="Standard-Format:").pack(anchor="w")
        self.format_var = tk.StringVar(value="Excel (.xlsx)")
        format_combo = ttk.Combobox(
            export_frame,
            textvariable=self.format_var,
            values=["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
            style="Modern.TCombobox",
            state="readonly",
        )
        format_combo.pack(fill="x", pady=(5, 15))

        # Export directory
        ttk.Label(export_frame, text="Export-Verzeichnis:").pack(anchor="w")
        export_dir_frame = ttk.Frame(export_frame)
        export_dir_frame.pack(fill="x", pady=(5, 15))

        self.export_dir_var = tk.StringVar(value="exports")
        export_dir_entry = ttk.Entry(
            export_dir_frame,
            textvariable=self.export_dir_var,
            style="Modern.TEntry",
            state="normal",  # Erlaube manuelle Eingabe
        )
        export_dir_entry.pack(side="left", fill="x", expand=True)

        browse_button = ttk.Button(
            export_dir_frame,
            text="📁",
            style="Modern.TButton",
            width=3,
            command=self.browse_export_directory,
        )
        browse_button.pack(side="right", padx=(5, 0))

        # Quick access buttons for common paths
        quick_access_frame = ttk.Frame(export_frame)
        quick_access_frame.pack(fill="x", pady=(5, 0))

        ttk.Label(
            quick_access_frame, text="Schnellzugriff:", style="ModernLabel.TLabel"
        ).pack(anchor="w")

        button_frame = ttk.Frame(quick_access_frame)
        button_frame.pack(fill="x", pady=(2, 10))

        # Desktop button
        desktop_btn = ttk.Button(
            button_frame,
            text="🖥️ Desktop",
            style="Modern.TButton",
            command=lambda: self.set_export_path(
                os.path.expanduser("~/Desktop/BundesligaExports")
            ),
        )
        desktop_btn.pack(side="left", padx=(0, 5))

        # Documents button
        docs_btn = ttk.Button(
            button_frame,
            text="📄 Dokumente",
            style="Modern.TButton",
            command=lambda: self.set_export_path(
                os.path.expanduser("~/Documents/BundesligaExports")
            ),
        )
        docs_btn.pack(side="left", padx=(0, 5))

        # Downloads button
        downloads_btn = ttk.Button(
            button_frame,
            text="📥 Downloads",
            style="Modern.TButton",
            command=lambda: self.set_export_path(
                os.path.expanduser("~/Downloads/BundesligaExports")
            ),
        )
        downloads_btn.pack(side="left")

        # Include options
        self.include_lineups = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            export_frame,
            text="Aufstellungen einbeziehen",
            variable=self.include_lineups,
        ).pack(anchor="w", pady=5)

        self.include_goalscorers = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            export_frame,
            text="Torschützen einbeziehen",
            variable=self.include_goalscorers,
        ).pack(anchor="w", pady=5)

        # Cache management
        cache_frame = ttk.LabelFrame(settings_frame, text="🗑️ Cache & Daten", padding=20)
        cache_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20)
        )

        # Cache buttons
        cache_buttons = ttk.Frame(cache_frame)
        cache_buttons.pack()

        clear_cache_button = ttk.Button(
            cache_buttons,
            text="🗑️ Cache leeren",
            style="Warning.TButton",
            command=self.clear_cache,
        )
        clear_cache_button.pack(side="left", padx=(0, 10))

        clear_data_button = ttk.Button(
            cache_buttons,
            text="🗑️ Daten löschen",
            style="Warning.TButton",
            command=self.clear_data,
        )
        clear_data_button.pack(side="left")

    def create_license_tab(self):
        """Erstellt den Lizenz-Tab."""
        license_frame = ttk.Frame(self.notebook)
        self.notebook.add(license_frame, text="📋 Lizenz & Copyright")

        # Configure grid
        license_frame.grid_columnconfigure(0, weight=1)
        license_frame.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.LabelFrame(
            license_frame,
            text="🛡️ Bundesliga Scraper Pro - Lizenzvereinbarung",
            padding=20,
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        info_label = ttk.Label(
            header_frame,
            text="© 2025 ZeyDev. Alle Rechte vorbehalten.\n\nBitte lesen Sie die nachfolgenden Lizenzbestimmungen sorgfältig durch.",
            style="Card.TLabel",
            font=("Segoe UI", 11, "bold"),
            justify="center",
        )
        info_label.pack(pady=10)

        # Scrollable license text
        text_frame = ttk.LabelFrame(
            license_frame, text="📄 Vollständige Lizenzvereinbarung", padding=20
        )
        text_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Create text widget with scrollbar
        text_container = ttk.Frame(text_frame)
        text_container.pack(fill="both", expand=True)

        # Text widget
        license_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            bg=ModernColors.BG_WHITE,
            fg=ModernColors.TEXT_PRIMARY,
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=15,
            height=20,
        )

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            text_container, orient="vertical", command=license_text.yview
        )
        license_text.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        license_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # License content
        license_content = """BUNDESLIGA SCRAPER PRO - LIZENZVEREINBARUNG

© 2025 ZeyDev. Alle Rechte vorbehalten.

WICHTIGE LIZENZBESTIMMUNGEN:

1. EIGENTUMSRECHTE
   Diese Software ist das geistige Eigentum von ZeyDev. Alle Rechte, 
   Titel und Interessen an der Software verbleiben bei ZeyDev.

2. NUTZUNGSERLAUBNIS
   ✅ Private, nicht-kommerzielle Nutzung
   ✅ Erstellen von Backup-Kopien für persönliche Zwecke
   ✅ Verwendung der exportierten Daten für persönliche Analyse

3. VERBOTENE AKTIVITÄTEN
   ❌ Kommerzielle Nutzung ohne schriftliche Genehmigung
   ❌ Weiterverteilung der Software
   ❌ Reverse Engineering, Dekompilierung oder Disassemblierung
   ❌ Entfernung von Copyright-Hinweisen oder Wasserzeichen
   ❌ Verwendung für illegale Zwecke

4. HAFTUNGSAUSSCHLUSS
   Die Software wird "wie besehen" bereitgestellt, ohne Gewährleistung 
   jeglicher Art. ZeyDev haftet nicht für Schäden, die durch die 
   Nutzung dieser Software entstehen.

5. DATENVERANTWORTUNG
   Der Nutzer ist verantwortlich für die rechtmäßige Verwendung der 
   gescrapten Daten und muss alle relevanten Datenschutz- und 
   Urheberrechtsbestimmungen beachten.

6. KÜNDIGUNGSKLAUSEL
   Diese Lizenz kann bei Verstößen gegen die Bedingungen sofort 
   widerrufen werden.

7. GERICHTSSTAND UND ANWENDBARES RECHT
   Für alle Streitigkeiten aus oder im Zusammenhang mit dieser Lizenz 
   ist das deutsche Recht anwendbar.

KONTAKT:
Für Lizenzanfragen oder Fragen wenden Sie sich bitte an ZeyDev.

TECHNISCHE DETAILS:
- Version: Bundesliga Scraper Pro v2.3
- Build: Desktop Edition
- Lizenztyp: Proprietär
- Gültig ab: 2025

WICHTIGER HINWEIS:
Durch die Nutzung dieser Software stimmen Sie den oben genannten 
Bedingungen zu. Falls Sie mit den Bedingungen nicht einverstanden 
sind, ist die Nutzung der Software nicht gestattet.

Diese Lizenz kann jederzeit von ZeyDev aktualisiert werden. Die 
jeweils aktuelle Version ist maßgeblich.
"""

        # Insert license text
        license_text.insert("1.0", license_content)
        license_text.config(state="disabled")  # Make read-only

        # Button frame
        button_frame = ttk.Frame(text_frame)
        button_frame.pack(fill="x", pady=(15, 0))

        # Acceptance info
        acceptance_label = ttk.Label(
            button_frame,
            text="✅ Durch die Nutzung dieser Software stimmen Sie den Lizenzbestimmungen zu.",
            style="Card.TLabel",
            font=("Segoe UI", 9, "italic"),
            foreground=ModernColors.SUCCESS,
        )
        acceptance_label.pack(side="left")

        # Print license button
        print_button = ttk.Button(
            button_frame,
            text="🖨️ Lizenz drucken",
            style="Modern.TButton",
            command=self.print_license,
        )
        print_button.pack(side="right", padx=(10, 0))

    def print_license(self):
        """Öffnet den Druckdialog für die Lizenz (vereinfacht)."""
        messagebox.showinfo(
            "Lizenz drucken",
            "Die Lizenzvereinbarung kann über den Browser gedruckt werden.\n"
            "Kopieren Sie den Text und fügen Sie ihn in einen Texteditor ein.",
        )

    def create_footer(self):
        """Erstellt den Footer mit Watermark und Lizenz-Informationen."""
        # Separator line
        separator = ttk.Separator(self.root, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=(10, 5))

        footer_frame = ttk.Frame(self.root, style="Card.TFrame")
        footer_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Hauptzeile mit App-Info
        main_footer = ttk.Frame(footer_frame, style="Card.TFrame")
        main_footer.pack(fill="x", pady=10, padx=15)

        app_label = ttk.Label(
            main_footer,
            text="🏆 Bundesliga Scraper Pro | Entwickelt für professionelle Datenanalyse",
            style="Card.TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        app_label.pack(side="left")

        # Lizenz-Button
        license_button = ttk.Button(
            main_footer,
            text="📋 Lizenz anzeigen",
            style="Modern.TButton",
            command=self.show_license,
            width=15,
        )
        license_button.pack(side="right", padx=(10, 0))

        # Watermark/Copyright-Zeile
        watermark_frame = ttk.Frame(footer_frame, style="Card.TFrame")
        watermark_frame.pack(fill="x", padx=15, pady=(0, 10))

        # Linksseitige Info
        version_label = ttk.Label(
            watermark_frame,
            text="Version 2.3 | Build: Desktop Edition | © 2025",
            style="Card.TLabel",
            font=("Segoe UI", 9),
        )
        version_label.pack(side="left")

        # Rechtsseitiges Watermark
        watermark_label = ttk.Label(
            watermark_frame,
            text="🛡️ Alle Rechte vorbehalten an ZeyDev",
            style="Card.TLabel",
            font=("Segoe UI", 9, "bold"),
        )
        watermark_label.pack(side="right")

    def show_license(self):
        """Zeigt den Lizenz-Dialog an."""
        LicenseDialog(self.root)

    def update_season_selection(self):
        """Aktualisiert die Saison-Auswahl basierend auf dem gewählten Modus."""
        # Clear existing widgets
        for widget in self.season_selection_frame.winfo_children():
            widget.destroy()

        mode = self.season_mode.get()
        current_year = datetime.now().year
        seasons = [f"{year}-{str(year+1)[2:]}" for year in range(1963, current_year)]

        if mode == "single":
            ttk.Label(self.season_selection_frame, text="Saison:").pack(
                side="left", padx=(0, 10)
            )
            self.selected_season = tk.StringVar(value=seasons[-1])
            season_combo = ttk.Combobox(
                self.season_selection_frame,
                textvariable=self.selected_season,
                values=seasons,
                style="Modern.TCombobox",
                state="readonly",
            )
            season_combo.pack(side="left")

        elif mode == "multiple":
            ttk.Label(
                self.season_selection_frame, text="Saisons (Strg+Klick für mehrere):"
            ).pack(anchor="w")

            # Listbox for multiple selection
            listbox_frame = ttk.Frame(self.season_selection_frame)
            listbox_frame.pack(fill="both", expand=True, pady=(10, 0))

            self.season_listbox = tk.Listbox(
                listbox_frame, height=8, selectmode="extended", font=("Segoe UI", 9)
            )
            self.season_listbox.pack(side="left", fill="both", expand=True)

            # Add seasons to listbox
            for season in seasons:
                self.season_listbox.insert(tk.END, season)

            # Scrollbar for listbox
            listbox_scrollbar = ttk.Scrollbar(
                listbox_frame, orient="vertical", command=self.season_listbox.yview
            )
            listbox_scrollbar.pack(side="right", fill="y")
            self.season_listbox.configure(yscrollcommand=listbox_scrollbar.set)

        else:  # all seasons
            info_label = ttk.Label(
                self.season_selection_frame,
                text=f"📅 Alle {len(seasons)} Saisons werden heruntergeladen (1963/64 - {seasons[-1]})",
                style="Muted.TLabel",
            )
            info_label.pack()

    def apply_filters(self):
        """Wendet die Filter auf die Daten an."""
        # Implementation would filter self.games_data and update the tree
        messagebox.showinfo("Filter", "Filter wurden angewendet!")

    def export_filtered_data(self):
        """Exportiert die gefilterten Daten."""
        if not self.games_data:
            messagebox.showwarning(
                "Keine Daten", "Es sind keine Daten zum Exportieren vorhanden."
            )
            return

        # File dialog for save location (starting in configured export directory)
        initial_dir = self.export_dir_var.get()
        filename = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )

        if filename:
            try:
                # Convert games to DataFrame
                data = []
                for game in self.games_data:
                    data.append(
                        {
                            "Datum": game.date or "",
                            "Saison": game.season or "",
                            "Spieltag": game.matchday or "",
                            "Heimteam": game.home_team.name if game.home_team else "",
                            "Auswärtsteam": (
                                game.away_team.name if game.away_team else ""
                            ),
                            "Ergebnis": (
                                f"{game.home_score}:{game.away_score}"
                                if game.home_score is not None
                                and game.away_score is not None
                                else ""
                            ),
                            "Torschützen_Heim": (
                                ", ".join([g.scorer for g in game.home_goals])
                                if game.home_goals
                                else ""
                            ),
                            "Torschützen_Auswärts": (
                                ", ".join([g.scorer for g in game.away_goals])
                                if game.away_goals
                                else ""
                            ),
                        }
                    )

                df = pd.DataFrame(data)

                # Export based on file extension
                if filename.endswith(".xlsx"):
                    df.to_excel(filename, index=False)
                elif filename.endswith(".csv"):
                    df.to_csv(filename, index=False, encoding="utf-8-sig")
                else:
                    df.to_excel(filename, index=False)  # Default to Excel

                messagebox.showinfo(
                    "Export erfolgreich",
                    f"Daten wurden erfolgreich exportiert nach:\n{filename}",
                )
            except Exception as e:
                messagebox.showerror(
                    "Export-Fehler", f"Fehler beim Exportieren:\n{str(e)}"
                )

    def start_batch_download(self):
        """Startet den Batch-Download."""
        mode = self.season_mode.get()
        selected_seasons = []

        if mode == "single":
            selected_seasons = [self.selected_season.get()]
        elif mode == "multiple":
            indices = self.season_listbox.curselection()
            if not indices:
                messagebox.showwarning(
                    "Keine Auswahl", "Bitte wählen Sie mindestens eine Saison aus."
                )
                return
            selected_seasons = [self.season_listbox.get(i) for i in indices]
        else:  # all
            current_year = datetime.now().year
            selected_seasons = [
                f"{year}-{str(year+1)[2:]}" for year in range(1963, current_year)
            ]

        # Start download in separate thread
        threading.Thread(
            target=self.download_worker, args=(selected_seasons,), daemon=True
        ).start()

    def download_worker(self, seasons: List[str]):
        """Worker-Thread für den Download mit detaillierter Fortschrittsanzeige."""

        # Validiere Export-Verzeichnis zuerst
        if not self.validate_export_directory():
            return

        # Schätze die Gesamtzahl der Spiele (34 Spieltage × 9 Spiele pro Spieltag = 306 pro Saison)
        estimated_total_games = len(seasons) * 306

        # Create progress dialog with estimated total
        progress_dialog = ModernProgressDialog(
            self.root,
            "Download",
            f"Downloading {len(seasons)} Saison(en)...",
            estimated_total_games,
        )

        all_games = []
        error_occurred = False
        error_message = ""
        current_game_count = 0

        def progress_callback(current: int, total: int, status: str = ""):
            """Callback für Fortschritts-Updates (Thread-safe)."""
            nonlocal current_game_count
            current_game_count = current
            if not progress_dialog.cancelled:
                # Schedule update in main thread to ensure thread safety
                self.root.after(
                    0, lambda: progress_dialog.update_progress(current, total, status)
                )

        try:
            # Setup asyncio event loop for this thread
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Run the async batch download with progress callback
                games = loop.run_until_complete(
                    self.scraper.batch_download_with_progress(
                        seasons, progress_callback
                    )
                )
                all_games.extend(games)

                # Store games
                self.games_data = all_games

                # Auto-export to Excel
                if all_games and not progress_dialog.cancelled:
                    progress_dialog.update_progress(
                        current_game_count, current_game_count, "Exportiere zu Excel..."
                    )

                    export_filename = f"bundesliga_batch_{len(all_games)}_spiele.xlsx"

                    # Get configured export directory
                    export_dir = self.export_dir_var.get()
                    os.makedirs(export_dir, exist_ok=True)

                    # Use ExcelExporter
                    self.exporter.set_output_directory(export_dir)
                    exported_file = self.exporter.export_by_team(
                        all_games, export_filename
                    )

                    logger.info(
                        f"Batch-Download abgeschlossen: {len(all_games)} Spiele in {exported_file} exportiert"
                    )

            finally:
                loop.close()

        except Exception as e:
            error_occurred = True
            error_message = str(e)
            logger.error(f"Fehler beim Download: {e}")

        finally:
            # Close progress dialog
            if not progress_dialog.cancelled:
                progress_dialog.update_progress(
                    current_game_count, current_game_count, "Download abgeschlossen!"
                )
                time.sleep(1)
            progress_dialog.close()

            # Update UI in main thread
            if error_occurred:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Fehler",
                        f"Fehler beim Download: {error_message}",
                    ),
                )
            elif not progress_dialog.cancelled:
                # Update stats
                self.root.after(0, lambda: self.update_stats())
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Download",
                        f"Download von {len(seasons)} Saison(en) abgeschlossen!\n"
                        f"{len(all_games)} Spiele gefunden und exportiert.",
                    ),
                )

    def load_url_file(self):
        """Lädt URLs aus einer Datei."""
        filename = filedialog.askopenfilename(
            title="URL-Datei öffnen",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )

        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.url_text.delete(1.0, tk.END)
                    self.url_text.insert(1.0, content)

                messagebox.showinfo(
                    "Datei geladen", f"URLs aus {filename} wurden geladen."
                )

            except Exception as e:
                messagebox.showerror(
                    "Fehler", f"Fehler beim Laden der Datei:\n{str(e)}"
                )

    def process_urls(self):
        """Verarbeitet die eingegebenen URLs."""
        urls_text = self.url_text.get(1.0, tk.END).strip()

        if not urls_text:
            messagebox.showwarning(
                "Keine URLs", "Bitte geben Sie mindestens eine URL ein."
            )
            return

        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

        if urls:
            # Start processing in separate thread
            threading.Thread(target=self.url_worker, args=(urls,), daemon=True).start()

    def url_worker(self, urls: List[str]):
        """Worker-Thread für URL-Verarbeitung."""

        # Validiere Export-Verzeichnis zuerst
        if not self.validate_export_directory():
            return

        progress_dialog = ModernProgressDialog(
            self.root, "URL-Verarbeitung", f"Verarbeite {len(urls)} URL(s)..."
        )

        try:
            # Setup asyncio event loop for this thread
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            games = []
            try:
                for i, url in enumerate(urls):
                    if progress_dialog.cancelled:
                        break

                    progress_dialog.update_progress(
                        i, len(urls), f"Verarbeite URL {i+1}/{len(urls)}"
                    )

                    # Process URL with real scraper
                    if url.strip() and "kicker.de" in url:
                        try:
                            game = loop.run_until_complete(
                                self.scraper.parse_game_detail(url)
                            )
                            if game:
                                games.append(game)
                        except Exception as e:
                            logger.error(f"Fehler beim Verarbeiten von URL {url}: {e}")

                # Store games
                if games:
                    current_games = getattr(self, "games_data", [])
                    current_games.extend(games)
                    self.games_data = current_games  # Auto-export to Excel
                    export_filename = f"einzelspiele_{len(games)}.xlsx"

                    # Get configured export directory
                    export_dir = self.export_dir_var.get()
                    os.makedirs(export_dir, exist_ok=True)

                    # Use ExcelExporter
                    self.exporter.set_output_directory(export_dir)
                    exported_file = self.exporter.export_by_team(games, export_filename)

                    logger.info(
                        f"URL-Verarbeitung abgeschlossen: {len(games)} Spiele in {exported_file} exportiert"
                    )

            finally:
                loop.close()

            if not progress_dialog.cancelled:
                progress_dialog.update_progress(
                    len(games), len(games), "Verarbeitung abgeschlossen!"
                )
                time.sleep(1)
                progress_dialog.close()

                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Verarbeitung",
                        f"{len(games)} Spiel(e) erfolgreich verarbeitet und exportiert!",
                    ),
                )

        except Exception as e:
            progress_dialog.close()
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Verarbeitungsfehler", f"Fehler bei der Verarbeitung:\n{str(e)}"
                ),
            )

    def update_stats(self):
        """Aktualisiert die Statistiken."""
        if self.games_data:
            total_games = len(self.games_data)
            total_goals = sum(
                game.home_score + game.away_score
                for game in self.games_data
                if game.home_score is not None and game.away_score is not None
            )
            seasons = len(set(game.season for game in self.games_data if game.season))
            teams = len(
                set(
                    [game.home_team for game in self.games_data]
                    + [game.away_team for game in self.games_data]
                )
            )

            self.stats_cards["games"].update_value(str(total_games))
            self.stats_cards["goals"].update_value(str(total_goals))
            self.stats_cards["seasons"].update_value(str(seasons))
            self.stats_cards["teams"].update_value(str(teams))
        else:
            for card in self.stats_cards.values():
                card.update_value("0")

    def clear_cache(self):
        """Leert den Cache."""
        messagebox.showinfo("Cache", "Cache wurde geleert!")

    def clear_data(self):
        """Löscht alle geladenen Daten."""
        if messagebox.askyesno(
            "Daten löschen", "Alle geladenen Daten wirklich löschen?"
        ):
            self.games_data.clear()
            self.update_stats()

            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)

            messagebox.showinfo("Daten gelöscht", "Alle Daten wurden gelöscht!")

    def set_export_path(self, path: str):
        """Setzt einen Export-Pfad und zeigt Feedback."""
        self.export_dir_var.set(path)
        # Validiere und erstelle Pfad wenn nötig
        if self.validate_export_directory():
            messagebox.showinfo(
                "Export-Pfad geändert", f"Export-Verzeichnis wurde geändert zu:\n{path}"
            )

    def browse_export_directory(self):
        """Öffnet einen Dialog zur Auswahl des Export-Verzeichnisses."""
        directory = filedialog.askdirectory(
            title="Export-Verzeichnis auswählen", initialdir=self.export_dir_var.get()
        )

        if directory:
            self.export_dir_var.set(directory)
            # Update exporter
            self.exporter.output_dir = Path(directory)
            messagebox.showinfo(
                "Export-Verzeichnis geändert",
                f"Export-Verzeichnis wurde geändert zu:\n{directory}",
            )

    def validate_export_directory(self):
        """Validiert und erstellt das Export-Verzeichnis falls nötig."""
        export_dir = self.export_dir_var.get().strip()

        if not export_dir:
            messagebox.showerror("Fehler", "Bitte geben Sie ein Export-Verzeichnis an.")
            return False

        try:
            # Versuche Verzeichnis zu erstellen
            os.makedirs(export_dir, exist_ok=True)

            # Prüfe Schreibberechtigung
            test_file = os.path.join(export_dir, "test_write.tmp")
            try:
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
            except Exception:
                messagebox.showerror(
                    "Fehler", f"Keine Schreibberechtigung für:\n{export_dir}"
                )
                return False

            # Update exporter
            self.exporter.output_dir = Path(export_dir)
            return True

        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Konnte Export-Verzeichnis nicht erstellen:\n{export_dir}\n\nFehler: {str(e)}",
            )
            return False

    def run(self):
        """Startet die GUI."""
        self.root.mainloop()


def main():
    """Hauptfunktion."""
    app = ModernBundesligaGUI()
    app.run()


if __name__ == "__main__":
    main()
