#!/bin/bash
# Git Setup Script für Bundesliga Scraper Pro
# Führen Sie diese Kommandos nacheinander aus

echo "🚀 Git Repository Setup für Bundesliga Scraper Pro"
echo "=================================================="

# 1. Git Repository initialisieren (falls noch nicht geschehen)
echo "📁 Initialisiere Git Repository..."
git init

# 2. Remote Repository hinzufügen (ERSETZEN SIE IHR_USERNAME)
echo "🔗 Füge Remote Repository hinzu..."
echo "⚠️  WICHTIG: Ersetzen Sie 'IHR_USERNAME' mit Ihrem GitHub-Benutzernamen!"
# git remote add origin https://github.com/IHR_USERNAME/bundesliga-scraper-pro.git

# 3. Alle Dateien zum Staging hinzufügen
echo "📦 Füge Dateien zum Staging hinzu..."
git add .

# 4. Initial Commit
echo "💾 Erstelle Initial Commit..."
git commit -m "🎉 Initial commit: Bundesliga Scraper Pro v2.4

✨ Features:
- 🎯 Dual GUI (Streamlit Web + Tkinter Desktop)
- ⚽ Vollständige Bundesliga-Daten von kicker.de
- 📊 Excel-Export mit Team-spezifischen Sheets
- 🚀 Konfigurierbare Download-Geschwindigkeit (4 Modi)
- 📈 Detaillierte Fortschrittsanzeige
- 🛡️ Rate Limiting zum Schutz vor Blockierung

🔧 Technologie:
- Python 3.8+ mit asyncio
- BeautifulSoup für HTML-Parsing
- pandas für Excel-Export
- Streamlit für Web-GUI
- ttkbootstrap für moderne Desktop-GUI

📋 Changelog v2.4:
- ✅ Export-Bug behoben (doppelte exports/exports)
- 🚀 Geschwindigkeits-Modi: 0.2s bis 2.0s pro Request
- 📊 Fortschritts-Tracking mit ETA und Geschwindigkeit
- 🎨 Modernes Desktop-Design mit ttkbootstrap"

# 5. Push zum Remote Repository (auskommentiert - manuell ausführen)
echo "🚀 Push zum Remote Repository..."
echo "⚠️  Führen Sie nach dem Remote-Setup aus:"
echo "     git push -u origin main"

echo ""
echo "✅ Git Setup abgeschlossen!"
echo ""
echo "📋 NÄCHSTE SCHRITTE:"
echo "1. Gehen Sie zu github.com und erstellen Sie ein neues PRIVATES Repository:"
echo "   - Name: bundesliga-scraper-pro"
echo "   - Description: 🏆 Bundesliga Scraper Pro - RESTRICTED ACCESS"
echo "   - Visibility: 🔒 PRIVATE (WICHTIG!)"
echo "   - ❌ NICHT initialisieren mit README (wir haben schon eins)"
echo ""
echo "2. Führen Sie dann diese Kommandos aus:"
echo "   git remote add origin https://github.com/Yigimon/Bundesliga-Scraper-.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Repository ist bereits erstellt unter: https://github.com/Yigimon/Bundesliga-Scraper-.git"
