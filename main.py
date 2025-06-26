"""
Bundesliga Scraper Pro - Main Entry Point
Bietet Auswahl zwischen Streamlit Web-GUI und Tkinter Desktop-GUI
"""

import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def start_streamlit():
    """Startet die Streamlit Web-GUI"""
    import subprocess

    app_path = project_root / "gui" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])


def start_tkinter():
    """Startet die Tkinter Desktop-GUI"""
    try:
        from gui.tkinter_app import ModernBundesligaGUI

        app = ModernBundesligaGUI()
        app.run()
    except ImportError as e:
        print(f"❌ Fehler beim Starten der Tkinter-GUI: {e}")
        print("Verwenden Sie die Option 1 für die Streamlit Web-GUI.")


def main():
    """Hauptmenü zur GUI-Auswahl"""
    print("🏆 Bundesliga Scraper Pro")
    print("=" * 40)
    print("Wählen Sie eine GUI-Option:")
    print("1. Streamlit Web-GUI (Browser)")
    print("2. Tkinter Desktop-GUI (Native)")
    print("3. Beenden")
    print("=" * 40)

    while True:
        choice = input("Ihre Wahl (1-3): ").strip()

        if choice == "1":
            print("🌐 Starte Streamlit Web-GUI...")
            start_streamlit()
            break
        elif choice == "2":
            print("🖥️ Starte Tkinter Desktop-GUI...")
            start_tkinter()
            break
        elif choice == "3":
            print("👋 Auf Wiedersehen!")
            sys.exit(0)
        else:
            print("❌ Ungültige Auswahl. Bitte wählen Sie 1, 2 oder 3.")


if __name__ == "__main__":
    main()
