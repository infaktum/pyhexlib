# PyHex — kurze interne Dokumentation

Dieses Dokument beschreibt kurz die reale Paketstruktur und die wichtigsten Klassen/Funktionen der `pyhex`
-Implementierung im Projekt. Es ersetzt die ältere, teilweise veraltete Beschreibung und richtet sich an Entwickler, die
in den Quellcode einsteigen möchten.

Hinweis: Die öffentliche README im Projekt-Root (`README.md`) enthält Benutzer- und Beispiel-Informationen; diese Datei
ist eher Entwickler-orientiert.

## Kernkonzepte

- Hexagon: In `pyhex` werden Hexagon-Koordinaten als Offset-Tupel `(row, col)` repräsentiert. Es existiert keine
  separate `Hex`-Objektklasse für jede Zelle — die Zellen werden durch ihre Koordinaten adressiert.
- Orientierung: Zwei Layouts werden unterstützt: `pyhex.basic.Orientation.FLAT` (flat-top) und
  `pyhex.basic.Orientation.POINTY` (pointy-top).

## Wichtige Module und Klassen

- `pyhex.basic`
    - Grundlegende Typen und Funktionen: `Orientation`, `Direction`, `Hexagon` (namedtuple `(row, col)`).
    - Koordinatenumrechnung: `offset_to_axial`, `axial_to_offset`, `distance`, `neighborhood_basic`.
    - Pfadfindungsfunktionen: `dijkstra`, `astar`.

- `pyhex.hexagons`
    - `HexagonalGrid`: leichte Container-Klasse, die eine Liste von Hex-Koordinaten verwaltet und Hilfsfunktionen
      bereitstellt (`bounds`, `size`, `axial_coordinates`, `neighbors`, `get_distance`, `path`).
    - Hilfsfunktion `rectangle(rows, cols)` zum Erzeugen eines rechteckigen Gitters.

- `pyhex.layers`
    - Layer-Typen für unterschiedliche Darstellungszwecke:
        - `HexGridManager`: Container für Hexagon-Sammlung und Layer; bietet `get_layer`, `add_layer`,
          `get_hexagons(clipping)` u.ä.
        - `FillGridLayer`, `OutlineGridLayer`, `StyledGridLayer` — Farb-/Stil-basierte Layer.
        - `SimpleImageGridLayer`, `TokenGridLayer`, `ImageGridLayer` — Bild/Token Layer.
        - `ValueGridLayer`, `TextGridLayer`, `CoordinateGridLayer`, `PathGridLayer`, `TerrainGridLayer`.

- `pyhex.graphic`
    - Pixel-/Geometrie-Hilfen: `hex_corner_with_offset`, `hex_corners`, `hex_dimensions`, `compute_screen_size`,
      `xy_to_rc`, `hex_center`, `compute_offset`.
    - Zeichenhilfen wie `draw_centered`, `rotate_image`.

- `pyhex.render`
    - `HexGridRenderer`: Der Renderer, der Layer rendert und einfache Caching-/Viewport-Funktionen bietet.
    - Standard-Renderfunktionen für Layer (z. B. `_render_outline_layer`, `_render_fill_layer`, `_render_image_layer`).

- `pyhex.assets`
    - Helfer zum Laden und Skalieren von Asset-Bildern, UI-Elementen und zur Vorhaltung von Bildressourcen.

## Logging

Die Bibliothek konfiguriert keine Ausgabe-Handler und hängt intern einen `logging.NullHandler` an den Paket-Logger.
Anwendungen sollen das Logging konfigurieren (z. B. mit `logging.basicConfig`) — die Beispiele in `examples/` zeigen
dieses Vorgehen.

## Kurze Gebrauchsanweisung (Beispiel)

Unten ein kleines, echtes Beispiel, wie man mit den vorhandenen Klassen ein Gitter anlegt und mit `HexGridRenderer`
rendert (Pygame):

```python
import pygame
import logging
import pyhex
from pyhex.hexagons import HexagonalGrid, rectangle_map
from pyhex.layers import HexGridManager, FillGridLayer, OutlineGridLayer, TokenGridLayer
from pyhex.render import HexGridRenderer
from pyhex import Orientation

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logging.getLogger('pyhex').setLevel(logging.DEBUG)

pygame.init()
pyhex.init(orientation=Orientation.FLAT, log_level=logging.DEBUG)

# Erzeuge ein Rechteckgitter 7x10
hexes = rectangle_map(7, 10)
grid = HexagonalGrid(hexes)

# Manager und Layer
manager = HexGridManager(grid)
manager.add_layer(FillGridLayer('background', default_color=(200, 200, 200)))
manager.add_layer(OutlineGridLayer('outline', default_color=(0, 0, 0), default_width=1))
manager.add_layer(TokenGridLayer('tokens'))

# Renderer mit Radius 50
renderer = HexGridRenderer(manager, radius=50)
screen = pygame.display.set_mode(renderer.screen_size)
renderer.render()
screen.blit(renderer.surface, (0, 0))
pygame.display.flip()

# einfacher Event-Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
```

## Hinweise für Entwickler

- Viele Dateinamen und APIs in früheren Dokumentationen sind veraltet (z. B. `hexagon.py`, `RenderEngine`). Verwende die
  hier genannten Module/Typen als aktuelle Referenz.
- Wenn Du Beispielcode zur README hinzufügen möchtest, orientiere Dich an den Dateien in `examples/`.

## Tests und Entwicklung

Siehe die Projekt-Root README für Hinweise zu virtuellen Umgebungen und Abhängigkeiten.
