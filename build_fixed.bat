@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM Bundesliga Scraper Pro - FIXED Build Script
REM Version: 3.1 (Error-Fixed)
REM ==========================================

title Bundesliga Scraper Pro - Build System v3.1 (FIXED)

color 0A
echo.
echo ==========================================
echo   BUNDESLIGA SCRAPER PRO - BUILD v3.1
echo ==========================================
echo   🔧 FIXED: PyInstaller Fehler behoben
echo   🚀 Modern GUI (Tkinter + Streamlit)
echo   📦 Standalone EXE Generation
echo ==========================================
echo.

REM Setze Variablen
set PROJECT_NAME=BundesligaScraperPro
set VERSION=3.1
set MAIN_FILE=main.py

REM Prüfe Python
echo 🔍 Prüfe Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nicht gefunden!
    pause
    exit /b 1
)
echo ✅ Python OK

REM Erstelle/Aktiviere venv
echo 📦 Virtual Environment...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo ✅ venv aktiviert

REM Upgrade pip
echo 📦 Upgrade pip...
python -m pip install --upgrade pip --quiet

REM Installiere Dependencies
echo 📦 Installiere Dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
) else (
    pip install httpx beautifulsoup4 lxml requests pandas openpyxl streamlit ttkbootstrap pyinstaller aiofiles typing-extensions --quiet
)

REM Prüfe PyInstaller speziell
echo 🔍 Prüfe PyInstaller...
python -c "import PyInstaller; print('PyInstaller OK')" 2>nul
if %errorlevel% neq 0 (
    echo 🔧 Installiere PyInstaller...
    pip install pyinstaller --force-reinstall
)

REM Bereinige alte Builds
echo 🧹 Bereinige...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "*.spec" del "*.spec" 2>nul

REM Einfacher PyInstaller Build
echo.
echo 🔨 Baue EXE (Einfacher Modus)...
python -m PyInstaller --onefile --noconsole --name="%PROJECT_NAME%" "%MAIN_FILE%"

REM Fallback wenn das fehlschlägt
if %errorlevel% neq 0 (
    echo ⚠️  Fallback: Verwende direkten pyinstaller...
    pyinstaller --onefile --noconsole --name="%PROJECT_NAME%" "%MAIN_FILE%"
)

REM Prüfe Ergebnis
if exist "dist\%PROJECT_NAME%.exe" (
    echo.
    echo ✅ BUILD ERFOLGREICH!
    echo 📁 EXE: dist\%PROJECT_NAME%.exe
    
    REM Erstelle Release
    if not exist "release" mkdir release
    copy "dist\%PROJECT_NAME%.exe" "release\"
    
    echo 📦 Release erstellt: release\%PROJECT_NAME%.exe
    echo.
    echo 🎉 Möchtest du den Release-Ordner öffnen? (J/N)
    set /p OPEN=
    if /i "!OPEN!"=="J" start explorer "release"
    
) else (
    echo ❌ BUILD FEHLGESCHLAGEN!
    echo Prüfe die Fehlermeldungen oben.
)

echo.
pause
