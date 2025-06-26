"""
Kicker.de HTML-Struktur-Analyse für moderne Spielschema-Seiten (2024/25)
=======================================================================

Basierend auf der Analyse der HTML-Datei:
"Spielschema ｜ Bor. Mönchengladbach - Bayer 04 Leverkusen 2：3 ｜ 1. Spieltag ｜ Bundesliga 2024_25"

WICHTIGE ERKENNTNISSE:
=====================

1. TORSCHÜTZEN-EXTRAKTION:
--------------------------

Hauptcontainer: section mit class="kick__section-item" und header h4="Tore"

Struktur für jeden Tor:
```html
<div class="kick__goals kick__goals--left">
    <span class="kick__goals__time">11'</span>
    <div class="kick__goals__team kick__goals__team--left">
        <a class="kick__goals__player" href="...">
            <span class="kick__substitutions--hide-mobile">Kleindienst</span>
        </a>
        <span class="kick__goals__player-subtxt"></span>
        <div class="kick__assist__player">
            <span>Kopfball nach Corner</span>
        </div>
    </div>
    <div class="kick__goals__score">
        <div class="kick__v100-scoreBoard kick__v100-scoreBoard--standard kick__v100-scoreBoard--goals__score">
            <div class="kick__v100-scoreBoard__scoreHolder kick__v100-scoreBoard__scoreHolder--transparent">
                <div class="kick__v100-scoreBoard__scoreHolder__score">1</div>
                <div class="kick__v100-scoreBoard__scoreHolder__divider">:</div>
                <div class="kick__v100-scoreBoard__scoreHolder__score">0</div>
            </div>
        </div>
    </div>
</div>
```

CSS-Selektoren für Torschützen:
- Container: 'section:has(h4:contains("Tore"))'
- Tor-Ereignisse: '.kick__goals'
- Spielername: '.kick__goals__player span'
- Zeit: '.kick__goals__time'
- Team-Seite: '.kick__goals__team--left' oder '.kick__goals__team--right'
- Art des Tors: '.kick__assist__player span'

2. AUFSTELLUNGEN-EXTRAKTION:
----------------------------

Hauptcontainer: section mit class="kick__section-item" und header h4="Aufstellung"

Struktur:
```html
<section class="kick__section-item">
    <header>
        <h4 class="kick__card-headline kick__text-center">Aufstellung</h4>
    </header>
    <div class="kick__data-grid kick__data-grid--half-r-s kick__lineup kick__lineup--player">
        <div class="kick__data-grid__main kick__data-grid__item--border-right">
            <div class="kick__lineup__team kick__lineup__team--left">
                <div class="kick__lineup-text">
                    <div class="kick__lineup-text__unorderedList">
                        <div><a href="...">Omlin<span class="kick__ticker-icon...">Captain</span><span class="kick__badge">2,5</span></a></div>
                        <div class="kick__lineup__trenner"><a href="...">Scally<span class="kick__badge">4,0</span></a></div>
                        <!-- Weitere Spieler... -->
                    </div>
                </div>
            </div>
        </div>
        <div class="kick__data-grid__main">
            <div class="kick__lineup__team kick__lineup__team--right">
                <!-- Rechtes Team analog -->
            </div>
        </div>
    </div>
</section>
```

CSS-Selektoren für Aufstellungen:
- Container: 'section:has(h4:contains("Aufstellung"))'
- Linkes Team: '.kick__lineup__team--left .kick__lineup-text__unorderedList'
- Rechtes Team: '.kick__lineup__team--right .kick__lineup-text__unorderedList'
- Spieler-Links: 'div > a[href*="/spieler/"]'
- Captain-Kennzeichnung: '.kick__icon-Captain_DICK'
- Bewertungen: '.kick__badge .kick__badge--note'

3. WEITERE WICHTIGE BEREICHE:
-----------------------------

WECHSEL:
- Container: 'section:has(h4:contains("Wechsel"))'
- Einwechslungen: '.kick__substitutions__cell--no-space' (grüner Pfeil)
- Auswechslungen: '.kick__substitutions__cell:not(.kick__substitutions__cell--no-space)' (roter Pfeil)

RESERVEBANK:
- Container: 'section:has(h4:contains("Reservebank"))'
- Ersatzspieler: Links innerhalb der Lineup-Text-Bereiche

KARTEN:
- Container: 'section:has(h4:contains("Karten"))'
- Gelbe Karten: '.kick__icon-Gelb'
- Rote Karten: '.kick__icon-Rot' (falls vorhanden)

4. BESONDERE MERKMALE:
----------------------

- Kapitäne werden mit span class="kick__icon-Captain_DICK" markiert
- Torschützen haben span class="kick__icon-Fussball" bei ihrem Namen
- Auswechslungen werden mit span class="kick__icon-Pfeil01" (rot) markiert
- Einwechslungen werden mit span class="kick__icon-Pfeil02" (grün) markiert
- Bewertungen stehen in span class="kick__badge--note"

5. ROBUST PARSING STRATEGIE:
============================

PRIMÄRE SELEKTOREN:
- Tore: 'section:has(header h4:contains("Tore")) .kick__goals'
- Aufstellung: 'section:has(header h4:contains("Aufstellung")) .kick__lineup__team'

FALLBACK-SELEKTOREN:
- Tore: '.kick__goals', '.kick__goals__player'
- Aufstellung: '.kick__lineup-text__unorderedList a[href*="/spieler/"]'

XPATH-ALTERNATIVEN:
- Tore: '//section[.//h4[contains(text(), "Tore")]]//div[@class="kick__goals"]'
- Aufstellung: '//section[.//h4[contains(text(), "Aufstellung")]]//a[contains(@href, "/spieler/")]'

6. DATENEXTRAKTION-PIPELINE:
============================

Für jeden Torschützen:
1. Zeit extrahieren (.kick__goals__time)
2. Spielername extrahieren (.kick__goals__player span)
3. Team-Zuordnung bestimmen (--left/--right)
4. Tor-Art extrahieren (.kick__assist__player span)

Für jede Aufstellung:
1. Team-Zuordnung bestimmen (--left/--right)
2. Alle Spieler-Links sammeln
3. Spielernamen aus Link-Text extrahieren
4. Captain/Bewertungen als Zusatzinfo

QUALITÄTSKONTROLLE:
- Prüfen ob 11 Feldspieler + 1 Torwart pro Team
- Validieren dass Torschützen in einer der Aufstellungen stehen
- Zeitangaben für Tore validieren (0-90+ Min)
"""
