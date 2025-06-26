@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM Bundesliga Scraper Pro v2.5 - Build Script
REM Erstellt eine optimierte .exe-Datei mit allen neuen Features
REM ==========================================

title Bundesliga Scraper Pro v2.5 - Build System

color 0A
echo.
echo ==========================================
echo   BUNDESLIGA SCRAPER PRO v2.5 - BUILD
echo ==========================================
echo   🚀 Modern GUI ^& Export Configuration
echo   ✨ Advanced Progress Indicators  
echo   📂 Configurable Export Paths
echo   🔐 License ^& Copyright Integration
echo ==========================================
echo.

REM === SYSTEM CHECKS ===
echo 🔍 System-Checks...

REM Prüfe Python-Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nicht gefunden! Bitte installieren Sie Python 3.8+
    echo    Download: https://python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% gefunden

REM Prüfe pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip nicht gefunden!
    pause
    exit /b 1
)

echo ✅ pip verfügbar

REM Prüfe Haupt-Script
if not exist "main.py" (
    echo ❌ main.py nicht gefunden!
    echo    Stellen Sie sicher, dass Sie im richtigen Projektverzeichnis sind.
    pause
    exit /b 1
)

echo ✅ main.py gefunden

REM Prüfe PyInstaller Spec
if not exist "bundesliga_scraper_pro.spec" (
    echo ❌ bundesliga_scraper_pro.spec nicht gefunden!
    echo    Build-Konfiguration fehlt.
    pause
    exit /b 1
)

echo ✅ Build-Konfiguration gefunden
echo.

REM === DEPENDENCIES ===
echo 📦 Installiere/Update Abhängigkeiten...

if not exist "requirements.txt" (
    echo ⚠️  requirements.txt nicht gefunden - verwende Standard-Dependencies
) else (
    echo    Installiere aus requirements.txt...
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo ❌ Fehler beim Installieren der Abhängigkeiten
        echo    Versuchen Sie: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM Prüfe PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installiere PyInstaller...
    pip install pyinstaller --quiet
    if errorlevel 1 (
        echo ❌ Fehler beim Installieren von PyInstaller
        pause
        exit /b 1
    )
)

echo ✅ Alle Abhängigkeiten installiert
echo.

REM === BUILD PREPARATION ===
echo 🔧 Build-Vorbereitung...

REM Erstelle Verzeichnisse
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM Lösche alte Builds
echo    Räume alte Builds auf...
if exist "dist\BundesligaScraperPro_v2.5.exe" (
    del "dist\BundesligaScraperPro_v2.5.exe"
    echo    ✅ Alte v2.5 .exe entfernt
)
if exist "dist\BundesligaScraperPro.exe" (
    del "dist\BundesligaScraperPro.exe"
    echo    ✅ Alte .exe entfernt
)
if exist "build\BundesligaScraperPro" (
    rmdir /s /q "build\BundesligaScraperPro"
    echo    ✅ Build-Cache geleert
)

echo ✅ Build-Umgebung vorbereitet
echo.

REM === MAIN BUILD PROCESS ===
echo 🔨 Starte Build-Prozess für v2.5...
echo.
echo    📋 Build-Features:
echo       ✨ Moderne Fortschrittsanzeige (exakte Spiele-Zählung)
echo       🎨 Dual-GUI System (Streamlit + Tkinter)
echo       📂 Konfigurierbare Export-Pfade
echo       🔐 Lizenz- und Copyright-Integration
echo       ⚡ Performance-Optimierungen
echo.
echo    ⏳ Dies kann 3-5 Minuten dauern...
echo.

REM Zeige aktuellen Zeitstempel
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set BUILD_TIME=%datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%
echo    🕐 Build gestartet: %BUILD_TIME%
echo.

REM PyInstaller Build mit v2.5 Spec
pyinstaller bundesliga_scraper_pro.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ❌ BUILD FEHLGESCHLAGEN!
    echo.
    echo 🔍 Häufige Probleme:
    echo    - Fehlende Dependencies: pip install -r requirements.txt
    echo    - Python-Version ^< 3.8: Upgrade auf Python 3.8+
    echo    - Speicher-Problem: Schließen Sie andere Programme
    echo    - Antivirenprogramm: Temporär deaktivieren
    echo.
    echo 📋 Prüfen Sie die Fehler oben und versuchen Sie es erneut.
    pause
    exit /b 1
)

REM === BUILD VERIFICATION ===
echo.
echo ✅ BUILD ERFOLGREICH ABGESCHLOSSEN!
echo.

REM Prüfe ob .exe erstellt wurde
if exist "dist\BundesligaScraperPro_v2.5.exe" (
    echo 🎉 BUNDESLIGA SCRAPER PRO v2.5 - BUILD KOMPLETT!
    echo.
    echo 📂 Executable: dist\BundesligaScraperPro_v2.5.exe
    
    REM Dateigröße anzeigen
    for %%A in ("dist\BundesligaScraperPro_v2.5.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1024/1024
        echo 📏 Dateigröße: !sizeMB! MB
    )
    
    REM Build-Zeit berechnen
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime2=%%I
    set END_TIME=%datetime2:~8,2%:%datetime2:~10,2%:%datetime2:~12,2%
    echo ⏱️  Fertiggestellt: %END_TIME%
    
    echo.
    echo ==========================================
    echo   🆕 NEUE FEATURES IN v2.5
    echo ==========================================
    echo   ✨ Exakte Fortschrittsanzeige
    echo      - Current/Total Spiele-Zählung
    echo      - Live-Zeitschätzung (MM:SS)
    echo      - 4-Metriken-Display
    echo.
    echo   🎨 Modernisierte GUIs
    echo      - Gradient-Design mit Hover-Effekten
    echo      - Responsive Layout
    echo      - Konsistente UX zwischen Web/Desktop
    echo.
    echo   📂 Export-Konfiguration
    echo      - Editierbare Export-Pfade
    echo      - Quick-Access-Buttons
    echo      - Automatische Pfad-Validierung
    echo.
    echo   🔐 Lizenz ^& Copyright
    echo      - Integrierte Lizenz-Anzeige
    echo      - Print-Funktion
    echo      - Rechtliche Klarstellung
    echo ==========================================
    echo.
    
    REM Test-Optionen
    echo 💡 Nächste Schritte:
    echo.
    set /p choice="   Möchten Sie die .exe jetzt testen? (j/n): "
    if /i "!choice!"=="j" (
        echo.
        echo 🚀 Starte BundesligaScraperPro_v2.5.exe...
        echo    Wählen Sie zwischen Streamlit (Web) oder Tkinter (Desktop) GUI
        start "" "dist\BundesligaScraperPro_v2.5.exe"
        echo.
        echo ✅ Anwendung gestartet!
    ) else (
        echo.
        echo 📁 Die .exe ist bereit zur Verwendung oder Verteilung
    )
    
    echo.
    echo 📋 Verwendung:
    echo    - Doppelklick auf die .exe-Datei
    echo    - Wählen Sie zwischen Web-GUI (Streamlit) oder Desktop-GUI (Tkinter)
    echo    - Für erste Nutzung: Standard-Geschwindigkeit empfohlen
    echo.
    
) else (
    echo ❌ .exe-Datei nicht gefunden!
    echo.
    echo 🔍 Mögliche Ursachen:
    echo    - Build-Prozess war nicht erfolgreich
    echo    - PyInstaller-Fehler (siehe Ausgabe oben)
    echo    - Antivirus hat .exe blockiert/gelöscht
    echo    - Insufficient disk space
    echo.
    echo 💡 Lösungsansätze:
    echo    - Nochmals bauen mit: build_pro.bat
    echo    - Antivirus temporär deaktivieren
    echo    - Freien Speicherplatz prüfen (min. 500MB)
    echo.
)

echo.
echo ==========================================
echo   BUILD-SCRIPT BEENDET
echo ==========================================
echo   Erstellt mit ❤️  für autorisierte Nutzer
echo   © 2024 @Yigimon - Bundesliga Scraper Pro
echo ==========================================

pause
