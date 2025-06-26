@echo off
REM Git Setup Script für Bundesliga Scraper Pro (Windows)
REM Führen Sie diese Kommandos nacheinander aus

echo 🚀 Git Repository Setup für Bundesliga Scraper Pro
echo ==================================================

REM 1. Git Repository initialisieren (falls noch nicht geschehen)
echo 📁 Initialisiere Git Repository...
git init

REM 2. Alle Dateien zum Staging hinzufügen
echo 📦 Füge Dateien zum Staging hinzu...
git add .

REM 3. Initial Commit
echo 💾 Erstelle Initial Commit...
git commit -m "🎉 Initial commit: Bundesliga Scraper Pro v2.4"

echo.
echo ✅ Git Setup abgeschlossen!
echo.
echo 📋 NÄCHSTE SCHRITTE:
echo 1. Gehen Sie zu github.com und erstellen Sie ein neues PRIVATES Repository:
echo    - Name: bundesliga-scraper-pro
echo    - Description: 🏆 Bundesliga Scraper Pro - RESTRICTED ACCESS
echo    - Visibility: 🔒 PRIVATE (WICHTIG!)
echo    - ❌ NICHT initialisieren mit README (wir haben schon eins)
echo.
echo 2. Führen Sie dann diese Kommandos aus:
echo    git remote add origin https://github.com/Yigimon/Bundesliga-Scraper-.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Repository ist bereits erstellt unter: https://github.com/Yigimon/Bundesliga-Scraper-.git
echo.
pause
