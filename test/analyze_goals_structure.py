"""
Spezifische Analyse der Tor-Struktur in der HTML-Datei
"""

from bs4 import BeautifulSoup
import re


def analyze_goals_structure():
    """Analysiert die spezifische Tor-Struktur in der HTML-Datei"""

    html_file_path = r"c:\Users\yigit\OneDrive\Desktop\CODING\Backup Kicker.de\kicker v2.3 muster\html\Spielschema ｜ Bor. Mönchengladbach - Bayer 04 Leverkusen 2：3 ｜ 1. Spieltag ｜ Bundesliga 2024_25 - kicker (24.6.2025 12：03：57).html"

    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    print("🔍 Suche nach Tor-Strukturen...")

    # 1. Suche nach Tore-Header
    print("\n1. Suche nach 'Tore' Headers:")
    h4_elements = soup.find_all("h4")
    for h4 in h4_elements:
        text = h4.get_text().strip()
        if "Tore" in text or "tore" in text.lower():
            print(f"   Gefunden: '{text}'")
            # Finde die übergeordnete Section
            section = h4.find_parent("section")
            if section:
                print(f"   Section Klassen: {section.get('class', [])}")

    # 2. Suche nach kick__goals Elementen
    print("\n2. Suche nach kick__goals Elementen:")
    goal_elements = soup.find_all("div", class_=re.compile(r".*goal.*"))
    print(f"   Gefundene Goal-Elemente: {len(goal_elements)}")

    for i, elem in enumerate(goal_elements[:3]):  # Nur die ersten 3
        print(f"   Element {i+1}:")
        print(f"     Klassen: {elem.get('class', [])}")
        print(f"     Text: {elem.get_text().strip()[:100]}...")

    # 3. Suche nach allen Sections und deren Header
    print("\n3. Alle Section-Header:")
    sections = soup.find_all("section", class_="kick__section-item")
    for i, section in enumerate(sections):
        header = section.find("header")
        if header:
            h4 = header.find("h4")
            if h4:
                text = h4.get_text().strip()
                print(f"   Section {i+1}: '{text}'")

                # Wenn es eine Tore-Section ist, analysiere sie detailliert
                if "Tore" in text:
                    print(f"     🎯 TORE-SECTION GEFUNDEN!")
                    print(f"     Section-Klassen: {section.get('class', [])}")

                    # Suche nach allen divs in dieser Section
                    all_divs = section.find_all("div")
                    print(f"     Anzahl divs in Section: {len(all_divs)}")

                    # Suche spezifisch nach goal-bezogenen Klassen
                    goal_divs = section.find_all("div", class_=re.compile(r".*goal.*"))
                    print(f"     Goal-divs: {len(goal_divs)}")

                    if goal_divs:
                        for j, div in enumerate(goal_divs):
                            print(f"       Goal-div {j+1}: {div.get('class', [])}")
                            print(f"       Text: {div.get_text().strip()[:50]}...")

    # 4. Volltext-Suche nach Spielernamen und Zeiten
    print("\n4. Volltext-Suche nach möglichen Torschützen:")
    full_text = soup.get_text()

    # Suche nach Zeit-Mustern gefolgt von Namen
    time_name_patterns = [
        r"(\d{1,2})'?\s*([A-ZÄÖÜ][a-zäöüß]+)",
        r"(\d{1,2})'[^\w]*([A-ZÄÖÜ][a-zäöüß]+)",
    ]

    for pattern in time_name_patterns:
        matches = re.finditer(pattern, full_text)
        for match in matches:
            minute = match.group(1)
            name = match.group(2)
            print(f"   {minute}': {name}")


if __name__ == "__main__":
    analyze_goals_structure()
