@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM Bundesliga Scraper Pro - ULTIMATE BUILD
REM Löst ALLE Probleme definitiv
REM GUI-Auswahlfenster + Alle Dependencies
REM ==========================================

title Bundesliga Scraper Pro - Ultimate Build v3.0

color 0D
echo.
echo ==========================================
echo   BUNDESLIGA SCRAPER PRO - ULTIMATE v3.0
echo ==========================================
echo   ✅ GUI-Auswahlfenster beim Start
echo   ✅ Alle Dependencies inklusive (pandas etc.)
echo   ✅ Stdin-Fehler komplett behoben
echo   ✅ Robuste Fehlerbehandlung
echo ==========================================
echo.

set PROJECT_NAME=BundesligaScraperPro_Ultimate

REM Python prüfen
echo 🔍 Prüfe Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nicht gefunden!
    pause
    exit /b 1
)
echo ✅ Python OK

REM Virtual Environment erstellen/aktivieren
echo 📦 Virtual Environment...
if not exist "venv" (
    echo 🔧 Erstelle venv...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo ✅ venv aktiviert

REM Pip upgraden
echo 📦 Upgrade pip...
python -m pip install --upgrade pip --quiet

REM ALLE Dependencies installieren
echo 📦 Installiere ALLE Dependencies...
pip install --quiet ^
    pandas ^
    openpyxl ^
    httpx ^
    beautifulsoup4 ^
    lxml ^
    requests ^
    streamlit ^
    ttkbootstrap ^
    aiofiles ^
    typing-extensions ^
    pyinstaller ^
    pathlib2 ^
    dataclasses

echo ✅ Alle Dependencies installiert

REM Bereinige
echo 🧹 Bereinige...
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
if exist "*.spec" del "*.spec" 2>nul

REM Erstelle umfassende PyInstaller Spec-Datei
echo 📝 Erstelle erweiterte Spec-Datei...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo import sys
echo from pathlib import Path
echo.
echo block_cipher = None
echo.
echo # Alle Daten-Dateien
echo datas = [
echo     ('gui', 'gui'^),
echo     ('scrapers', 'scrapers'^),
echo     ('exporters', 'exporters'^),
echo     ('models', 'models'^),
echo     ('config', 'config'^),
echo ]
echo.
echo # Umfassende Hidden Imports
echo hiddenimports = [
echo     # Tkinter
echo     'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
echo     'tkinter.scrolledtext', 'tkinter.font',
echo     # GUI Libraries
echo     'ttkbootstrap', 'ttkbootstrap.constants', 'ttkbootstrap.style',
echo     # Data Processing
echo     'pandas', 'pandas.core', 'pandas.io', 'pandas.io.excel',
echo     'openpyxl', 'openpyxl.workbook', 'openpyxl.worksheet',
echo     # Web Scraping
echo     'httpx', 'httpx._client', 'httpx._config',
echo     'beautifulsoup4', 'bs4', 'lxml', 'lxml.etree', 'lxml.html',
echo     'requests', 'requests.adapters', 'requests.packages',
echo     # Async
echo     'asyncio', 'aiofiles',
echo     # Standard Libraries
echo     'pathlib', 'dataclasses', 'typing_extensions',
echo     'datetime', 'json', 'csv', 'os', 'sys',
echo     # Project Modules
echo     'gui.app', 'gui.tkinter_app',
echo     'scrapers.kicker_scraper', 'scrapers.improved_kicker_scraper', 'scrapers.base_scraper',
echo     'exporters.excel_exporter_new', 'exporters.merge_service',
echo     'models.game_data', 'models.extended_data',
echo     'config.settings_manager',
echo ]
echo.
echo a = Analysis(
echo     ['main.py'],
echo     pathex=['.'],
echo     binaries=[],
echo     datas=datas,
echo     hiddenimports=hiddenimports,
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='%PROJECT_NAME%',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=False,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
) > "%PROJECT_NAME%.spec"

echo ✅ Spec-Datei erstellt

REM Baue mit Spec-Datei
echo.
echo 🔨 Baue Ultimate EXE...
echo    (Dies kann 3-5 Minuten dauern...)
python -m PyInstaller --clean "%PROJECT_NAME%.spec"

if exist "dist\%PROJECT_NAME%.exe" (
    echo.
    echo ✅ BUILD ERFOLGREICH!
    echo 📁 EXE: dist\%PROJECT_NAME%.exe
    
    REM Berechne Größe
    for %%A in ("dist\%PROJECT_NAME%.exe") do set EXE_SIZE=%%~zA
    set /a EXE_SIZE_MB=!EXE_SIZE!/1024/1024
    echo 📏 Größe: !EXE_SIZE_MB! MB
    
    REM Erstelle Release
    if not exist "release" mkdir release
    copy "dist\%PROJECT_NAME%.exe" "release\"
    
    REM Erstelle Anleitung
    (
    echo ==========================================
    echo  BUNDESLIGA SCRAPER PRO - ULTIMATE v3.0
    echo ==========================================
    echo.
    echo 🚀 SCHNELLSTART:
    echo    1. Doppelklick auf %PROJECT_NAME%.exe
    echo    2. GUI-Auswahlfenster erscheint
    echo    3. Wähle zwischen Desktop GUI oder Web GUI
    echo    4. Scrape deine Bundesliga-Daten!
    echo.
    echo ✅ FEATURES:
    echo    ✓ GUI-Auswahlfenster beim Start
    echo    ✓ Alle Dependencies inklusive
    echo    ✓ Keine pandas/stdin-Fehler mehr
    echo    ✓ Moderne Benutzeroberfläche
    echo.
    echo 🔧 PROBLEMBEHANDLUNG:
    echo    - Bei Antivirus-Warnung: Als sicher markieren
    echo    - Bei Startproblemen: Als Administrator ausführen
    echo.
    echo 📅 Build: %date% %time%
    echo ==========================================
    ) > "release\ULTIMATE_ANLEITUNG.txt"
    
    echo.
    echo 🎉 ULTIMATE BUILD ABGESCHLOSSEN!
    echo    📁 EXE: release\%PROJECT_NAME%.exe
    echo    📏 Größe: !EXE_SIZE_MB! MB
    echo    📝 Anleitung: release\ULTIMATE_ANLEITUNG.txt
    echo.
    echo    🚀 Jetzt sollten ALLE Probleme behoben sein!
    
    set /p TEST=Möchtest du die Ultimate EXE testen? (J/N): 
    if /i "!TEST!"=="J" start "Ultimate Test" "release\%PROJECT_NAME%.exe"
    
    set /p OPEN=Release-Ordner öffnen? (J/N): 
    if /i "!OPEN!"=="J" start explorer "release"
    
) else (
    echo ❌ BUILD FEHLGESCHLAGEN!
    echo    Prüfe die Ausgabe für Details.
)

echo.
pause
