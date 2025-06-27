@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM Bundesliga Scraper Pro - Comprehensive Build Script
REM Version: 3.0
REM Datum: %date%
REM ==========================================

title Bundesliga Scraper Pro - Build System v3.0

color 0A
echo.
echo ==========================================
echo   BUNDESLIGA SCRAPER PRO - BUILD v3.0
echo ==========================================
echo   🚀 Modern GUI (Tkinter + Streamlit)
echo   📊 Excel Export mit Formatierung
echo   🔍 Erweiterte Filter & Statistiken
echo   📦 Standalone EXE Generation
echo   🛠️ Auto-Dependency Management
echo ==========================================
echo.

REM Setze Variablen
set PROJECT_NAME=BundesligaScraperPro
set VERSION=3.0
set BUILD_DIR=build
set DIST_DIR=dist
set SPEC_FILE=%PROJECT_NAME%.spec
set MAIN_FILE=main.py
set ICON_FILE=assets\icon.ico
set DATA_FILES=config;gui;scrapers;exporters;models;assets

REM Prüfe ob Python verfügbar ist
echo 🔍 Prüfe Python-Installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python ist nicht installiert oder nicht im PATH!
    echo    Bitte installiere Python 3.8+ und füge es zum PATH hinzu.
    pause
    exit /b 1
)

REM Zeige Python-Version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% gefunden

REM Prüfe ob pip verfügbar ist
echo 🔍 Prüfe pip-Installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip ist nicht verfügbar!
    pause
    exit /b 1
)
echo ✅ pip verfügbar

REM Erstelle Virtual Environment falls nicht vorhanden
echo.
echo 📦 Erstelle/Aktiviere Virtual Environment...
if not exist "venv" (
    echo 🔧 Erstelle neues Virtual Environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Fehler beim Erstellen des Virtual Environment!
        pause
        exit /b 1
    )
)

REM Aktiviere Virtual Environment
echo 🔧 Aktiviere Virtual Environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Fehler beim Aktivieren des Virtual Environment!
    pause
    exit /b 1
)
echo ✅ Virtual Environment aktiviert

REM Upgrade pip
echo.
echo 📦 Upgrade pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  pip upgrade fehlgeschlagen, setze fort...
)

REM Installiere/Update Dependencies
echo.
echo 📦 Installiere/Update Dependencies...
if exist "requirements.txt" (
    echo 🔧 Installiere aus requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Fehler beim Installieren der Dependencies!
        pause
        exit /b 1
    )
) else (
    echo 🔧 Installiere Standard-Dependencies...
    pip install httpx beautifulsoup4 lxml requests pandas openpyxl streamlit ttkbootstrap pyinstaller aiofiles typing-extensions
    if %errorlevel% neq 0 (
        echo ❌ Fehler beim Installieren der Dependencies!
        pause
        exit /b 1
    )
)
echo ✅ Dependencies installiert

REM Prüfe Hauptdatei
echo.
echo 🔍 Prüfe Projektstruktur...
if not exist "%MAIN_FILE%" (
    echo ❌ Hauptdatei %MAIN_FILE% nicht gefunden!
    pause
    exit /b 1
)
echo ✅ Hauptdatei gefunden: %MAIN_FILE%

REM Prüfe wichtige Verzeichnisse
set MISSING_DIRS=
if not exist "gui" set MISSING_DIRS=!MISSING_DIRS! gui
if not exist "scrapers" set MISSING_DIRS=!MISSING_DIRS! scrapers
if not exist "exporters" set MISSING_DIRS=!MISSING_DIRS! exporters
if not exist "models" set MISSING_DIRS=!MISSING_DIRS! models

if not "!MISSING_DIRS!"=="" (
    echo ❌ Fehlende Verzeichnisse: !MISSING_DIRS!
    echo    Bitte überprüfe die Projektstruktur.
    pause
    exit /b 1
)
echo ✅ Projektstruktur vollständig

REM Erstelle Assets-Verzeichnis falls nicht vorhanden
if not exist "assets" (
    echo 🔧 Erstelle assets-Verzeichnis...
    mkdir assets
)

REM Erstelle Standard-Icon falls nicht vorhanden
if not exist "%ICON_FILE%" (
    echo 🔧 Erstelle Standard-Icon...
    echo. > assets\icon.ico
)

REM Bereinige alte Build-Artefakte
echo.
echo 🧹 Bereinige alte Build-Artefakte...
if exist "%BUILD_DIR%" (
    echo 🗑️  Lösche %BUILD_DIR%...
    rmdir /s /q "%BUILD_DIR%" 2>nul
)
if exist "%DIST_DIR%" (
    echo 🗑️  Lösche %DIST_DIR%...
    rmdir /s /q "%DIST_DIR%" 2>nul
)
if exist "%SPEC_FILE%" (
    echo 🗑️  Lösche alte .spec-Datei...
    del "%SPEC_FILE%" 2>nul
)
if exist "__pycache__" (
    echo 🗑️  Lösche __pycache__...
    rmdir /s /q "__pycache__" 2>nul
)

REM Lösche __pycache__ in Unterverzeichnissen
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo 🗑️  Lösche %%d...
        rmdir /s /q "%%d" 2>nul
    )
)
echo ✅ Build-Artefakte bereinigt

REM Führe Tests durch (falls vorhanden)
echo.
echo 🧪 Führe Tests durch...
if exist "test" (
    echo 🔧 Führe Tests im test-Verzeichnis aus...
    python -m pytest test/ -v 2>nul
    if %errorlevel% neq 0 (
        echo ⚠️  Tests fehlgeschlagen oder pytest nicht installiert
        echo    Setze Build trotzdem fort...
    ) else (
        echo ✅ Tests erfolgreich
    )
) else if exist "tests" (
    echo 🔧 Führe Tests im tests-Verzeichnis aus...
    python -m pytest tests/ -v 2>nul
    if %errorlevel% neq 0 (
        echo ⚠️  Tests fehlgeschlagen oder pytest nicht installiert
        echo    Setze Build trotzdem fort...
    ) else (
        echo ✅ Tests erfolgreich
    )
) else (
    echo ⚠️  Keine Tests gefunden, überspringe...
)

REM Erstelle PyInstaller Spec-Datei
echo.
echo 📝 Erstelle PyInstaller Spec-Datei...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo import sys
echo from pathlib import Path
echo.
echo block_cipher = None
echo.
echo # Daten-Dateien sammeln
echo datas = [
echo     ('gui', 'gui'^),
echo     ('scrapers', 'scrapers'^),
echo     ('exporters', 'exporters'^),
echo     ('models', 'models'^),
echo     ('config', 'config'^),
echo ]
echo.
echo # Versteckte Imports
echo hiddenimports = [
echo     'tkinter',
echo     'tkinter.ttk',
echo     'ttkbootstrap',
echo     'streamlit',
echo     'httpx',
echo     'beautifulsoup4',
echo     'pandas',
echo     'openpyxl',
echo     'lxml',
echo     'requests',
echo     'aiofiles',
echo     'asyncio',
echo     'pathlib',
echo     'dataclasses',
echo     'typing_extensions',
echo     'gui.app',
echo     'gui.tkinter_app',
echo     'scrapers.kicker_scraper',
echo     'scrapers.improved_kicker_scraper',
echo     'exporters.excel_exporter_new',
echo     'exporters.merge_service',
echo     'models.game_data',
echo     'models.extended_data',
echo     'config.settings_manager',
echo ]
echo.
echo a = Analysis(
echo     [r'%MAIN_FILE%'],
echo     pathex=[r'%cd%'],
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
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
echo.
echo # Erstelle auch eine Konsolen-Version für Debug
echo exe_console = EXE(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='%PROJECT_NAME%_Console',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=True,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
) > "%SPEC_FILE%"
echo ✅ Spec-Datei erstellt: %SPEC_FILE%

REM Prüfe ob PyInstaller verfügbar ist
echo.
echo 🔍 Prüfe PyInstaller-Installation...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PyInstaller nicht gefunden, installiere...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ PyInstaller-Installation fehlgeschlagen!
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller verfügbar

REM Baue die EXE-Datei
echo.
echo 🔨 Baue EXE-Datei...
echo    Dies kann einige Minuten dauern...
python -m PyInstaller --clean "%SPEC_FILE%"

if %errorlevel% neq 0 (
    echo ❌ Build fehlgeschlagen!
    echo    Versuche alternativen PyInstaller-Aufruf...
    pyinstaller --clean "%SPEC_FILE%"
    if %errorlevel% neq 0 (
        echo ❌ Build definitiv fehlgeschlagen!
        echo    Prüfe die Ausgabe für Details.
        pause
        exit /b 1
    )
)

REM Prüfe ob EXE erstellt wurde
if not exist "dist\%PROJECT_NAME%.exe" (
    echo ❌ EXE-Datei wurde nicht erstellt!
    pause
    exit /b 1
)

REM Berechne EXE-Größe
for %%A in ("dist\%PROJECT_NAME%.exe") do set EXE_SIZE=%%~zA
set /a EXE_SIZE_MB=%EXE_SIZE%/1024/1024

echo.
echo ✅ Build erfolgreich abgeschlossen!
echo.
echo ==========================================
echo   BUILD ZUSAMMENFASSUNG
echo ==========================================
echo   📦 Projekt: %PROJECT_NAME%
echo   🔢 Version: %VERSION%
echo   📁 EXE-Datei: dist\%PROJECT_NAME%.exe
echo   📏 Größe: %EXE_SIZE_MB% MB
echo   🕒 Erstellt: %date% %time%
echo ==========================================
echo.

REM Erstelle Release-Ordner mit zusätzlichen Dateien
echo 📦 Erstelle Release-Paket...
if not exist "release" mkdir release
copy "dist\%PROJECT_NAME%.exe" "release\"
if exist "dist\%PROJECT_NAME%_Console.exe" copy "dist\%PROJECT_NAME%_Console.exe" "release\"
if exist "README.md" copy "README.md" "release\"
if exist "LICENSE" copy "LICENSE" "release\"
if exist "UPDATE_v2.4_ZUSAMMENFASSUNG.md" copy "UPDATE_v2.4_ZUSAMMENFASSUNG.md" "release\"

REM Erstelle Start-Anleitung
(
echo ==========================================
echo  BUNDESLIGA SCRAPER PRO v%VERSION%
echo ==========================================
echo.
echo 🚀 SCHNELLSTART:
echo    1. Doppelklick auf %PROJECT_NAME%.exe
echo    2. Die Desktop-GUI startet automatisch
echo    3. Wähle Saison und Verein
echo    4. Klicke "Daten laden" oder "Alle Daten laden"
echo    5. Export wird automatisch erstellt
echo.
echo � ALTERNATIVE VERSIONEN:
echo    - %PROJECT_NAME%.exe: Desktop-GUI (empfohlen^)
echo    - %PROJECT_NAME%_Console.exe: Mit Konsole für Debug
echo.
echo �📋 SYSTEMANFORDERUNGEN:
echo    - Windows 7/8/10/11
echo    - Mindestens 4 GB RAM
echo    - Internetverbindung für Scraping
echo.
echo 🔧 PROBLEMBEHANDLUNG:
echo    - Bei Antivirus-Warnung: Datei als sicher markieren
echo    - Bei Startproblemen: Als Administrator ausführen
echo    - Bei GUI-Problemen: Konsolen-Version verwenden
echo    - Support: GitHub Repository
echo.
echo 📅 Version: %VERSION%
echo 📅 Build: %date%
echo ==========================================
) > "release\ANLEITUNG.txt"

echo ✅ Release-Paket erstellt: release\

REM Öffne Release-Ordner
echo.
echo 🎉 Build abgeschlossen!
echo    Möchtest du den Release-Ordner öffnen? (J/N^)
set /p OPEN_FOLDER=

if /i "!OPEN_FOLDER!"=="J" (
    start explorer "release"
)

REM Deaktiviere Virtual Environment
echo.
echo 🔧 Deaktiviere Virtual Environment...
call venv\Scripts\deactivate.bat 2>nul

echo.
echo 🎯 Build-Prozess vollständig abgeschlossen!
echo    EXE-Datei: release\%PROJECT_NAME%.exe
echo    Größe: %EXE_SIZE_MB% MB
echo.
pause
