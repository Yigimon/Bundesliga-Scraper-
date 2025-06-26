#!/usr/bin/env python3
"""
Download-Geschwindigkeits-Konfiguration für den Bundesliga Scraper.

Hier können Sie die Download-Parameter einfach anpassen:
"""

# Download-Geschwindigkeits-Profile
SPEED_PROFILES = {
    "sehr_schnell": {
        "rate_limit_delay": 0.2,  # 0.2 Sekunden zwischen Requests
        "description": "Sehr schnell - höchstes Risiko für Rate Limiting",
        "estimated_time_per_season": "2-3 Minuten",
    },
    "schnell": {
        "rate_limit_delay": 0.5,  # 0.5 Sekunden zwischen Requests
        "description": "Schnell - moderates Risiko",
        "estimated_time_per_season": "4-6 Minuten",
    },
    "standard": {
        "rate_limit_delay": 1.0,  # 1 Sekunde zwischen Requests (current default)
        "description": "Standard - sicher und zuverlässig",
        "estimated_time_per_season": "8-10 Minuten",
    },
    "langsam": {
        "rate_limit_delay": 2.0,  # 2 Sekunden zwischen Requests
        "description": "Langsam - maximale Sicherheit",
        "estimated_time_per_season": "15-20 Minuten",
    },
}

# Aktuell verwendetes Profil (ändern Sie dies nach Bedarf)
CURRENT_PROFILE = (
    "sehr_schnell"  # Optionen: "sehr_schnell", "schnell", "standard", "langsam"
)


def get_current_config():
    """Gibt die aktuelle Konfiguration zurück"""
    return SPEED_PROFILES[CURRENT_PROFILE]


def get_rate_limit_delay():
    """Gibt das aktuelle Rate Limit Delay zurück"""
    return SPEED_PROFILES[CURRENT_PROFILE]["rate_limit_delay"]


def list_all_profiles():
    """Listet alle verfügbaren Profile auf"""
    print("🚀 Verfügbare Download-Geschwindigkeits-Profile:\n")

    for profile_name, config in SPEED_PROFILES.items():
        current_marker = " ← AKTUELL" if profile_name == CURRENT_PROFILE else ""
        print(f"{profile_name.upper()}{current_marker}")
        print(f"  Verzögerung: {config['rate_limit_delay']}s zwischen Requests")
        print(f"  Beschreibung: {config['description']}")
        print(f"  Geschätzte Zeit pro Saison: {config['estimated_time_per_season']}")
        print()


if __name__ == "__main__":
    list_all_profiles()
    print(
        f"💡 Um die Geschwindigkeit zu ändern, bearbeiten Sie die Variable CURRENT_PROFILE in dieser Datei."
    )
    print(
        f"   Aktuelle Einstellung: {CURRENT_PROFILE} ({get_rate_limit_delay()}s Verzögerung)"
    )
