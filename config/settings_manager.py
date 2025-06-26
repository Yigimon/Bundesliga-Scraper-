"""
Settings Manager für Bundesliga Scraper Pro
Verwaltet Benutzereinstellungen wie Download-Pfad, Export-Optionen, etc.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class SettingsManager:
    """Verwaltet die Anwendungseinstellungen."""

    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = Path(settings_file)
        self.default_settings = {
            # Export-Einstellungen
            "export_directory": "exports",
            "export_format": "Excel (.xlsx)",
            "include_lineups": True,
            "include_goalscorers": True,
            "include_cards": False,
            # Scraper-Einstellungen
            "request_delay": 1.0,
            "timeout": 10,
            "retry_attempts": 3,
            "max_parallel_downloads": 3,
            "speed_profile": "Normal",
            # GUI-Einstellungen
            "default_gui": "streamlit",  # oder "tkinter"
            "auto_open_exports": True,
            "show_progress_details": True,
            # Erweiterte Einstellungen
            "cache_enabled": True,
            "log_level": "INFO",
            "max_log_files": 5,
        }

        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Lädt die Einstellungen aus der Datei."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)

                # Merge mit Default-Einstellungen (für neue Optionen)
                settings = self.default_settings.copy()
                settings.update(saved_settings)
                return settings

            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warnung: Konnte Einstellungen nicht laden: {e}")
                return self.default_settings.copy()
        else:
            return self.default_settings.copy()

    def save_settings(self):
        """Speichert die aktuellen Einstellungen."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Holt eine Einstellung."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Setzt eine Einstellung."""
        self.settings[key] = value

    def update(self, new_settings: Dict[str, Any]):
        """Aktualisiert mehrere Einstellungen."""
        self.settings.update(new_settings)

    def reset_to_defaults(self):
        """Setzt alle Einstellungen auf Standard zurück."""
        self.settings = self.default_settings.copy()

    # Convenience-Methoden für häufig verwendete Einstellungen

    def get_export_directory(self) -> str:
        """Holt das Export-Verzeichnis."""
        return self.get("export_directory", "exports")

    def set_export_directory(self, directory: str):
        """Setzt das Export-Verzeichnis."""
        # Erstelle das Verzeichnis falls es nicht existiert
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.set("export_directory", directory)
        self.save_settings()

    def get_export_format(self) -> str:
        """Holt das Export-Format."""
        return self.get("export_format", "Excel (.xlsx)")

    def set_export_format(self, format_str: str):
        """Setzt das Export-Format."""
        self.set("export_format", format_str)
        self.save_settings()

    def get_scraper_settings(self) -> Dict[str, Any]:
        """Holt alle Scraper-Einstellungen."""
        return {
            "request_delay": self.get("request_delay", 1.0),
            "timeout": self.get("timeout", 10),
            "retry_attempts": self.get("retry_attempts", 3),
            "max_parallel_downloads": self.get("max_parallel_downloads", 3),
            "speed_profile": self.get("speed_profile", "Normal"),
        }

    def update_scraper_settings(self, settings: Dict[str, Any]):
        """Aktualisiert die Scraper-Einstellungen."""
        scraper_keys = [
            "request_delay",
            "timeout",
            "retry_attempts",
            "max_parallel_downloads",
            "speed_profile",
        ]

        for key in scraper_keys:
            if key in settings:
                self.set(key, settings[key])

        self.save_settings()

    def get_include_options(self) -> Dict[str, bool]:
        """Holt die Include-Optionen für den Export."""
        return {
            "include_lineups": self.get("include_lineups", True),
            "include_goalscorers": self.get("include_goalscorers", True),
            "include_cards": self.get("include_cards", False),
        }

    def update_include_options(self, options: Dict[str, bool]):
        """Aktualisiert die Include-Optionen."""
        include_keys = ["include_lineups", "include_goalscorers", "include_cards"]

        for key in include_keys:
            if key in options:
                self.set(key, options[key])

        self.save_settings()

    def create_export_filename(self, base_name: str, extension: str = None) -> str:
        """Erstellt einen vollständigen Export-Dateinamen."""
        if extension is None:
            format_str = self.get_export_format()
            if "xlsx" in format_str:
                extension = ".xlsx"
            elif "csv" in format_str:
                extension = ".csv"
            elif "json" in format_str:
                extension = ".json"
            else:
                extension = ".xlsx"

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}{extension}"

        export_dir = Path(self.get_export_directory())
        return str(export_dir / filename)

    def get_export_path(self, filename: str) -> str:
        """Erstellt den vollständigen Pfad für eine Export-Datei."""
        export_dir = Path(self.get_export_directory())
        export_dir.mkdir(parents=True, exist_ok=True)
        return str(export_dir / filename)


# Globale Settings-Instanz
_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """Holt die globale Settings-Manager-Instanz."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_export_directory() -> str:
    """Convenience-Funktion für Export-Verzeichnis."""
    return get_settings_manager().get_export_directory()


def set_export_directory(directory: str):
    """Convenience-Funktion zum Setzen des Export-Verzeichnisses."""
    get_settings_manager().set_export_directory(directory)


def create_export_filename(base_name: str, extension: str = None) -> str:
    """Convenience-Funktion zum Erstellen von Export-Dateinamen."""
    return get_settings_manager().create_export_filename(base_name, extension)


def get_export_path(filename: str) -> str:
    """Convenience-Funktion für Export-Pfade."""
    return get_settings_manager().get_export_path(filename)
