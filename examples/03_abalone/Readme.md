# Abalone 

Dieser Ordner enthält das Beispiel `Abalone` mit der Spielimplementierung und Demo-Assets.

Dieses Beispiel zeigt folgende Features der PyHex-Bibliothek:

- Hexagonales Spielfeld mit spezieller Startaufstellung.
- Verwendung **grafischer Spielsteine** (`Tokens`)
- Anzeige von möglichen Zügen durch **Markierung von Feldern**
- Spielmechanik mit Mehrfachsteinbewegungen und Schieberegeln (Sumito).
- **Negative Koordinaten** für Spielfeldpositionen - das Zentrum des Feldes hat die Koordinate (0, 0).
- Einfache KI-Gegner (Minimax-Algorithmus).

## Spielregeln

- Spielbrett: Hexagonales Raster mit 61 Feldern.
- Spieler: 2 (jeweils eine Farbe).
- Ziel: Schiebe 6 gegnerische Steine vom Brett.
- Züge:
  - Einzel- oder Mehrfachsteinzug: 1, 2 oder 3 eigene Steine können bewegt werden.
  - Zwei Zugarten:
    - Inline-Move (in Linienrichtung): Kann gegnerische Steine schieben (Sumito), wenn die bewegende Gruppe numerisch überlegen ist.
    - Side-Move (seitlich/parallel): Bewegt Gruppe ohne Schieben des Gegners.
- **Sumito**-Regeln: Eine Gruppe von n eigenen Steinen kann 1 oder 2 gegnerische Steine in Bewegungsrichtung schieben, sofern keine andere Hindernisse im Weg sind; wird ein Stein vom Brett geschoben, zählt er als gefangen.


## Projektstruktur (kurz)

- 
Kurzbeschreibung
- Umsetzung des Brettspiels *Abalone* auf einer hexagonalen Spielfläche mit der PyHex-Infrastruktur.
- Ziel: Steine des Gegners vom Spielfeld schieben (insgesamt 6 Steine gewinnen).

## Installation & Start
1. Voraussetzungen: Python 3.8+ und pip.
2. Abhängigkeiten installieren:
3. Demo/Spiel starten:
   - Im Projekt-Root das Beispielskript in diesem Ordner ausführen (z.\ B.\ `python examples/03_abalone/main.py`), falls vorhanden.


## Nützliche Links
- Abalone (Wikipedia): https://en.wikipedia.org/wiki/Abalone_(board_game)
- BoardGameGeek (Abalone): https://boardgamegeek.com/boardgame/121/abalone
- Pygame (Grafik/Events): https://www.pygame.org/docs/


