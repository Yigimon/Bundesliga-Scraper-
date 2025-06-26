# Copilot Prompt: Bundesliga-Scraper mit moderner GUI, Excel-Export & Filter-Dashboard
## **Wenn von dir neue Dateien erstellt werden die alte ersetzen soll, dann lösche die alten versionen**
## ""Wenn test dateien oder dergleichen (degug, test, alles was nicht mit dem Hauptprogramm zutun hat) erstellt werden, die nicht für die hauptanwendung relevant sind speichere sie in einem seperaten ordner mit dem namen test ab**
## lösche niemals den **.github ordner mit seinen inhalten**
## Projektziel
Erzeuge eine Desktop-Anwendung (Windows-.exe) mit minimalistischem, modernem UI/UX, die für jede Bundesliga-Saison (1963/64 bis heute) alle Spiele eines Vereins in Excel-Tabellen exportiert, inklusive:
- Heimteam, Auswärtsteam, Datum, Ergebnis
- Torschützen und Startaufstellungen beider Teams  
- Automatischer Batch-Download aller Vereine  
- Option, einzelne oder mehrere Spiele manuell hinzuzufügen  
- Home-Dashboard mit Filtern (Saison, Verein, Datum, Tore-Range) und Statistiken (meiste Tore, meiste Siege, Top-Torschützen)

## Technischer Überblick
1. **HTTP-Core**  

     ```  
   - **Alle Spiele einer Saison auf einen Blick**:  
     ```
     GET https://www.kicker.de/bundesliga/spieltag/{Saison}/-1
     ```  
     Beispiel:  
     > https://www.kicker.de/bundesliga/spieltag/1963-64/-1  
   - Einzels-Spieltag-Liste:  
     ```
     GET https://www.kicker.de/bundesliga/spieltag/{Saison}/{Spieltag}
     ```  
   - **Detail-Aufrufe je Spiel** (für jede Partie auf der Spieltag-Seite muss auf „Schema“ geklickt werden, um Aufstellung und Torschützen auszulesen):  
     ```
     Klick „Schema“ → GET https://www.kicker.de/{heim}-gegen-{gast}-{jahr}-bundesliga-{ID}/schema
     ```  
     Beispiel:  
     > https://www.kicker.de/muenchen-gegen-braunschweig-1963-bundesliga-20087/schema  
   - Aus den Detail-Seiten ziehen:  
     - **Torschützen**: aus dem Abschnitt „Tore“ (Schema-Seite)  
     - **Aufstellungen**: aus dem Abschnitt „Aufstellung“ (Schema-Seite)

2. **Architektur**  
   - `BaseScraper` (OOP, abstrakte Methoden `analyze_structure()`, `fetch()`, `parse()`)  
   - `KickerScraper` (erbt von `BaseScraper`, implementiert Bundesliga-Logik)  
   - `DataManager` (Dataclasses/Typisierung, hält Spiel-Objekte)  
   - `ExcelExporter` (Gruppiert nach Verein, erstellt pro Verein ein Sheet; klar formatierte Spalten, lesbar ohne Extra-Klick)  
   - `MergeService` (nimmt existierende Excel, fügt neue Datensätze hinzu)

3. **GUI & UX**  
   - Technologie: **Streamlit** oder **Tkinter + ttkbootstrap**  
   - **Home-Seite**:  
     - Dropdown für Saison & Verein  
     - Buttons: „Alle Daten laden“, „Spiele hinzufügen“  
     - Filter-Panel: Datum-Range, Tore-Min/Max, Torschützen-Name  
     - Statistik-Kacheln:  
       - 🔢 Meiste Tore Gesamt & pro Saison  
       - 🏆 Meiste Siege  
       - 👟 Top-Torschützen  
   - **Batch-Download-Flow**:  
     1. Klick „Alle Daten laden“ → Scraper lädt sequenziell pro Spieltag  
     2. Fortschrittsbalken + Status-Log  
     3. Export in Excel + Download-Button  
   - **Einzelspiel-Flow**:  
     - Textfeld für Spiel-URL(s) oder CSV-Import  
     - Klick „Importieren & Exportieren“

4. **Performance & Packaging**  
   - Asynchrone Requests (z. B. `httpx` + `asyncio`)  
   - Caching lokaler HTML-Strukturen für Wiederholungs-Läufe  
   - Bundling mit **PyInstaller ––onefile**, damit nur eine `.exe` entsteht  
   - Ressourcen (Icons, Templates) eingebettet über `sys._MEIPASS`

5. **Erweiterbarkeit**  
   - Weitere Scraper leicht per Vererbung integrierbar (`TransfermarktScraper`, etc.)  
   - GUI-Module modulare Komponenten (Streamlit-Pages oder Tkinter-Frames)

---

```python
# Starte hier: boilerplate.py

"""
# BundesligaScraperApp
Main entry point: startet GUI und orchestriert Scraping & Export.
"""

import asyncio
import sys
from gui import App  # Gui-Module mit Streamlit oder Tkinter
from scrapers import KickerScraper
from exporter import ExcelExporter
from merge_service import MergeService

def main():
    # 1. GUI starten
    app = App(
        scraper=KickerScraper(),
        exporter=ExcelExporter(),
        merger=MergeService(),
    )
    app.run()

if __name__ == "__main__":
    main()
python
Kopieren
Bearbeiten
# scrapers/base_scraper.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseScraper(ABC):
    @abstractmethod
    def analyze_structure(self, url: str) -> Dict[str, Any]:
        """Einmalige Analyse, um DOM-Struktur zu erkennen."""
        pass

    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Lädt HTML asynchron."""
        pass

    @abstractmethod
    def parse(self, html: str) -> Dict[str, Any]:
        """Extrahiert Spiel-Daten robust und redundant."""
        pass

    @abstractmethod
    async def batch_download(self, seasons: List[str]) -> List[Dict[str, Any]]:
        """Lädt alle Spiele einer Saison per Spieltag."""
        pass
Stichpunkte für Copilot:

Implementiere KickerScraper mit httpx.AsyncClient

Nutze BeautifulSoup für redundantes Parsing, setze Fallback-Selektoren

ExcelExporter mit pandas.ExcelWriter, formatiere Spaltenbreite und Zellen-Styles

GUI: Streamlit-Layout mit Sidebar-Filtern, Progress Bar, Download-Button

Packe alles in eine Onefile-Exe via PyInstaller-Spec