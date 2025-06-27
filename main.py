"""
Bundesliga Scraper Pro - GUI Selector
Zeigt ein Auswahlfenster für Desktop GUI vs Web GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import subprocess
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class GUISelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bundesliga Scraper Pro - GUI Auswahl")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        # Zentriere das Fenster
        self.center_window()

        # Style
        self.root.configure(bg="#f0f0f0")

        self.setup_ui()

    def center_window(self):
        """Zentriert das Fenster auf dem Bildschirm"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🏆 Bundesliga Scraper Pro",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        title_label.pack(pady=20)

        # Main content
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Beschreibung
        desc_label = tk.Label(
            main_frame,
            text="Wählen Sie Ihre bevorzugte Benutzeroberfläche:",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#2c3e50",
        )
        desc_label.pack(pady=(0, 20))

        # Button Frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=10)

        # Desktop GUI Button
        desktop_btn = tk.Button(
            button_frame,
            text="🖥️ Desktop GUI\n(Tkinter - Nativ)",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            relief="flat",
            width=20,
            height=3,
            command=self.start_desktop_gui,
            cursor="hand2",
        )
        desktop_btn.pack(pady=10)

        # Web GUI Button
        web_btn = tk.Button(
            button_frame,
            text="🌐 Web GUI\n(Streamlit - Browser)",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            width=20,
            height=3,
            command=self.start_web_gui,
            cursor="hand2",
        )
        web_btn.pack(pady=10)

        # Info Text
        info_text = tk.Text(
            main_frame,
            height=4,
            width=50,
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Arial", 9),
            relief="flat",
            state="normal",
        )
        info_text.pack(pady=(20, 0))

        info_content = """💡 Empfehlung:
• Desktop GUI: Schneller, direkter Start, native Windows-Oberfläche
• Web GUI: Moderne Weboberfläche, läuft im Browser, mehr Features

🔧 Bei Problemen: Wählen Sie die Desktop GUI für beste Kompatibilität."""

        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")

        # Beenden Button
        quit_btn = tk.Button(
            main_frame,
            text="❌ Beenden",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            width=15,
            command=self.quit_app,
            cursor="hand2",
        )
        quit_btn.pack(pady=(10, 0))

    def start_desktop_gui(self):
        """Startet die Desktop GUI"""
        try:
            from gui.tkinter_app import ModernBundesligaGUI

            self.root.destroy()  # Schließe Auswahlfenster
            app = ModernBundesligaGUI()
            app.run()
        except ImportError as e:
            messagebox.showerror(
                "Fehler",
                f"Desktop GUI konnte nicht gestartet werden:\n{e}\n\nBitte versuchen Sie die Web GUI.",
            )
        except Exception as e:
            messagebox.showerror(
                "Fehler", f"Unerwarteter Fehler beim Starten der Desktop GUI:\n{e}"
            )

    def start_web_gui(self):
        """Startet die Web GUI"""
        try:
            self.root.destroy()  # Schließe Auswahlfenster
            app_path = project_root / "gui" / "app.py"
            subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
        except FileNotFoundError:
            messagebox.showerror(
                "Fehler",
                "Streamlit ist nicht installiert oder die GUI-Datei wurde nicht gefunden.\n\nBitte versuchen Sie die Desktop GUI.",
            )
        except Exception as e:
            messagebox.showerror(
                "Fehler", f"Unerwarteter Fehler beim Starten der Web GUI:\n{e}"
            )

    def quit_app(self):
        """Beendet die Anwendung"""
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """Startet die GUI-Auswahl"""
        self.root.mainloop()


def main():
    """Hauptfunktion - startet GUI-Auswahl"""
    try:
        selector = GUISelector()
        selector.run()
    except Exception as e:
        # Fallback wenn GUI-Selector fehlschlägt
        print(f"GUI-Selector Fehler: {e}")
        print("Starte Desktop GUI als Fallback...")
        try:
            from gui.tkinter_app import ModernBundesligaGUI

            app = ModernBundesligaGUI()
            app.run()
        except Exception as fallback_error:
            print(f"Fallback fehlgeschlagen: {fallback_error}")
            sys.exit(1)


if __name__ == "__main__":
    main()
