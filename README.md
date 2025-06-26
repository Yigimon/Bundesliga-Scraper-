# Bundesliga Scraper Pro 🏆

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-Streamlit%20%26%20Tkinter-red.svg)](https://streamlit.io)
[![Access](https://img.shields.io/badge/Access-Authorized%20Only-orange.svg)](LICENSE)

> **🔒 RESTRICTED ACCESS - AUTHORIZED USERS ONLY**  
> **Desktop & Web GUI für Kicker.de Bundesliga-Daten mit Excel-Export und konfigurierbarer Download-Geschwindigkeit**

## ⚠️ IMPORTANT - ACCESS RESTRICTIONS

**🚨 THIS SOFTWARE IS FOR AUTHORIZED USERS ONLY 🚨**

- ✅ **Authorized Access Required**: Only persons explicitly authorized by @Yigimon may use this software
- ❌ **No Public Access**: Unauthorized use is strictly prohibited and may result in legal action
- 🔒 **Proprietary License**: This is not open source software - see [LICENSE](LICENSE) for details
- 📝 **Contact Required**: For access authorization, contact @Yigimon on GitHub

**If you are not an authorized user, you must stop using this software immediately.**

## 🌟 Features

### 🎯 Kernfunktionen
- **Vollständige Saison-Downloads** von kicker.de (1963/64 bis heute)
- **Einzelspiel-Import** über URLs oder CSV
- **Excel-Export** mit Team-spezifischen Sheets
- **Zwei moderne GUIs**: Streamlit (Web) & Tkinter (Desktop)
- **Konfigurierbare Download-Geschwindigkeit** (0.2s - 2.0s pro Request)

### 📊 Datenextraktion
- ⚽ **Torschützen** mit Minute und Schussart
- 👥 **Startaufstellungen** (exakt 11 Spieler pro Team)
- 📅 **Spieldetails** (Datum, Saison, Spieltag, Ergebnis)
- 🏟️ **Team-Zuordnung** automatisch

### 🚀 Performance
- **4 Geschwindigkeitsmodi**: Sehr schnell (2-3 Min) bis Sicher (15-20 Min) pro Saison
- **Rate Limiting** zum Schutz vor Blockierung
- **Asynchrone Downloads** für bessere Performance
- **Fortschrittsanzeige** mit Zeitschätzung

## 📥 Installation (Authorized Users Only)

### ⚠️ Prerequisites
- **Authorization Required**: You must be explicitly authorized by @Yigimon to use this software
- Python 3.8+
- Windows (getestet), macOS/Linux (sollte funktionieren)
- Valid authorization from @Yigimon

### 1. Authorization Check
**Before proceeding, ensure you have explicit permission to use this software.**  
Unauthorized use is prohibited and may result in legal action.

### 2. Repository Access (Private Repository)
```bash
# Only for authorized users with repository access
git clone https://github.com/Yigimon/Bundesliga-Scraper-.git
cd Bundesliga-Scraper-
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Anwendung starten
```bash
python main.py
```

**Note**: If you encounter access issues, verify your authorization status.

## 🎮 Verwendung

### GUI-Auswahl
Beim Start können Sie zwischen zwei GUIs wählen:

1. **Streamlit Web-GUI** - Moderne Browser-Oberfläche
2. **Tkinter Desktop-GUI** - Native Windows-Anwendung

### Download-Modi

#### 📊 Batch-Download (Komplette Saisons)
- Wählen Sie eine oder mehrere Saisons
- Automatischer Download aller 306 Spiele pro Saison
- Export in strukturierte Excel-Dateien

#### 🎯 Einzelspiel-Import
- Fügen Sie kicker.de Schema-URLs hinzu
- CSV-Import für mehrere Spiele
- Flexible Datenergänzung

### ⚙️ Geschwindigkeits-Konfiguration

Bearbeiten Sie `config/speed_config.py`:

```python
CURRENT_PROFILE = "schnell"  # Optionen: "sehr_schnell", "schnell", "standard", "langsam"
```

| Modus | Verzögerung | Zeit/Saison | Empfehlung |
|-------|-------------|-------------|------------|
| Sehr Schnell | 0.2s | 2-3 Min | ⚠️ Nur für Tests |
| Schnell | 0.5s | 4-6 Min | 🏃 Optimal |
| Standard | 1.0s | 8-10 Min | ✅ Sicher |
| Langsam | 2.0s | 15-20 Min | 🛡️ Maximal sicher |

## 📁 Projektstruktur

```
bundesliga-scraper-pro/
├── 📱 gui/
│   ├── app.py                 # Streamlit Web-GUI
│   └── tkinter_app.py         # Desktop-GUI (ttkbootstrap)
├── 🔧 scrapers/
│   ├── base_scraper.py        # Abstract Base Class
│   ├── kicker_scraper.py      # Haupt-Scraper (vollständig)
│   └── improved_kicker_scraper.py # Experimentell
├── 📊 exporters/
│   ├── excel_exporter_new.py  # Excel-Export-Engine
│   └── merge_service.py       # Datei-Merge-Service
├── 🏗️ models/
│   └── game_data.py           # Datenstrukturen
├── ⚙️ config/
│   └── speed_config.py        # Download-Geschwindigkeits-Konfiguration
├── 📂 exports/                # Generierte Excel-Dateien
├── 🧪 test/                   # Test-Skripte
└── 📋 requirements.txt        # Python-Dependencies
```

## 🚨 Troubleshooting

### Rate Limiting erkannt
1. Stoppen Sie den Download
2. Warten Sie 1-2 Minuten  
3. Wechseln Sie zu einem langsameren Modus
4. Starten Sie den Download neu

### Export-Probleme
- Stellen Sie sicher, dass der `exports/` Ordner existiert
- Prüfen Sie die Schreibberechtigung im Projektordner

### GUI-Probleme
- **Streamlit**: `pip install streamlit` und Port 8501 freigeben
- **Tkinter**: `pip install ttkbootstrap` für modernes Design

## 🛠️ Entwicklung

### Tests ausführen
```bash
python test/test_export_fix.py
python config/speed_config.py  # Zeigt aktuelle Konfiguration
```

### Neue Geschwindigkeitsprofile
Erstellen Sie eigene Profile in `config/speed_config.py`:

```python
"custom": {
    "rate_limit_delay": 0.3,
    "description": "Mein Profil",
    "estimated_time_per_season": "5-7 Minuten"
}
```

## 📈 Performance-Tipps

- **Starten Sie mit "Standard"** für die erste Nutzung
- **"Schnell"** ist optimal für regelmäßige Nutzung  
- **Desktop-GUI** läuft effizienter als Web-GUI
- **Stabile Internetverbindung** verbessert Erfolgsrate

## 🏆 Changelog

### v2.4 (Latest)
- ✅ **Export-Bug behoben**: Keine doppelten exports/exports Ordner mehr
- 🚀 **Konfigurierbare Geschwindigkeit**: 4 Modi von 0.2s bis 2.0s
- 📊 **Detaillierte Fortschrittsanzeige**: Zeit, Geschwindigkeit, ETA
- 🎨 **Modernes Desktop-GUI**: ttkbootstrap-Design

### v2.3
- 📱 Dual-GUI System (Streamlit + Tkinter)
- 📊 Erweiterte Excel-Exports mit Team-Sheets
- 🔄 Verbesserte Datenextraktion

## 📄 Lizenz

**PROPRIETARY LICENSE - RESTRICTED ACCESS**

Dieses Projekt steht unter einer **proprietären Lizenz mit eingeschränktem Zugang**. Siehe [LICENSE](LICENSE) für vollständige Details.

**Wichtige Punkte:**
- 🔒 **Nur autorisierte Benutzer** - Kein öffentlicher Zugang gestattet
- ❌ **Kein Open Source** - Kopieren, Verteilung oder Modifikation verboten
- 📝 **Schriftliche Autorisierung erforderlich** - Kontaktieren Sie den Copyright-Inhaber
- ⚖️ **Rechtsschutz** - Verstöße unterliegen rechtlichen Schritten

## 🔐 Zugang & Autorisierung

**Diese Software ist proprietär und zugangsgesteuert.**

### 🔐 Autorisierung erhalten
- Kontaktieren Sie **@Yigimon** (GitHub) für Zugangsautorisierung
- Begründung für beabsichtigte Nutzung bereitstellen
- Zustimmung zu den in der LIZENZ angegebenen Bedingungen
- Kommerzielle Nutzung erfordert separate schriftliche Autorisierung

### 📋 Pflichten autorisierter Benutzer
- Nur für autorisierte Zwecke verwenden
- Nicht teilen, kopieren oder verteilen ohne Erlaubnis
- robots.txt und Nutzungsbedingungen von kicker.de respektieren
- Unbefugte Nutzung **@Yigimon** melden

### ⚠️ Verstöße
Unbefugte Nutzung stellt eine Urheberrechtsverletzung dar und kann zur Folge haben:
- Sofortiger Entzug des Zugangs
- Rechtliche Schritte für Schadenersatz  
- Strafverfolgung wo anwendbar

## ⚠️ Haftungsausschluss

⚠️ **WICHTIG**: Dieses Tool ist **NUR FÜR AUTORISIERTE BENUTZER** bestimmt und nur für persönliche, nicht-kommerzielle Nutzung gedacht. Respektieren Sie die robots.txt und Nutzungsbedingungen von kicker.de.

**UNBEFUGTE NUTZUNG IST VERBOTEN UND KANN RECHTLICHE SCHRITTE ZUR FOLGE HABEN.**

---

**🔒 Made with ⚽ for authorized Bundesliga fans only**

**For access authorization, contact @Yigimon on GitHub: https://github.com/Yigimon**
