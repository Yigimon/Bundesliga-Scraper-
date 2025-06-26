@echo off
REM ==========================================
REM Bundesliga Scraper Pro - Build Script
REM Erstellt eine optimierte .exe-Datei
REM ==========================================

title Bundesliga Scraper Pro - Build

echo.
echo ==========================================
echo  BUNDESLIGA SCRAPER PRO - BUILD SCRIPT
echo ==========================================
echo.

REM Prüfe Python-Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nicht gefunden! Bitte installieren Sie Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python gefunden
echo.

REM Prüfe pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip nicht gefunden!
    pause
    exit /b 1
)

echo ✅ pip gefunden
echo.

REM Installiere/Update Requirements
echo 📦 Installiere Abhängigkeiten...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Fehler beim Installieren der Abhängigkeiten
    pause
    exit /b 1
)

echo ✅ Abhängigkeiten installiert
echo.

REM Prüfe PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installiere PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Fehler beim Installieren von PyInstaller
        pause
        exit /b 1
    )
)

echo ✅ PyInstaller bereit
echo.

REM Erstelle Build-Verzeichnis falls nicht vorhanden
if not exist "dist" mkdir dist
if not exist "build" mkdir build

REM Lösche alte Builds
echo 🗑️ Räume alte Builds auf...
if exist "dist\BundesligaScraperPro.exe" del "dist\BundesligaScraperPro.exe"
if exist "build\BundesligaScraperPro" rmdir /s /q "build\BundesligaScraperPro"

echo.
echo 🔨 Starte Build-Prozess...
echo    Dies kann einige Minuten dauern...
echo.

REM PyInstaller Build mit optimierter Spec
pyinstaller bundesliga_scraper_pro.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ❌ Build fehlgeschlagen!
    echo    Prüfen Sie die Fehler oben und versuchen Sie es erneut.
    pause
    exit /b 1
)

echo.
echo ✅ Build erfolgreich!

REM Prüfe ob .exe erstellt wurde
if exist "dist\BundesligaScraperPro.exe" (
    echo ✅ Executable erstellt: dist\BundesligaScraperPro.exe
    
    REM Dateigröße anzeigen
    for %%A in ("dist\BundesligaScraperPro.exe") do (
        set size=%%~zA
        set /a sizeMB=!size!/1024/1024
        echo 📏 Dateigröße: !sizeMB! MB
    )
    
    echo.
    echo 🎉 BUILD ABGESCHLOSSEN!
    echo.
    echo 📂 Die .exe-Datei befindet sich in: dist\BundesligaScraperPro.exe
    echo 🚀 Sie können die Datei jetzt ausführen oder verteilen.
    echo.
    
    REM Frage ob .exe gestartet werden soll
    set /p choice="💡 Möchten Sie die .exe jetzt testen? (j/n): "
    if /i "%choice%"=="j" (
        echo.
        echo 🚀 Starte BundesligaScraperPro.exe...
        start "" "dist\BundesligaScraperPro.exe"
    )
    
) else (
    echo ❌ .exe-Datei nicht gefunden!
    echo    Der Build war möglicherweise nicht erfolgreich.
)

echo.
echo ==========================================
echo  BUILD-SCRIPT BEENDET
echo ==========================================
pause
