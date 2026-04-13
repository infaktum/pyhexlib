import pygame

from pyhex.assets import Assets


# -------------------------------------------- Assets -------------------------------------------------

class GameAssets(Assets):
    def __init__(self, size):
        super().__init__(size)
        self.images = {
            0: draw_token(size, (255, 0, 0)),
            1: draw_token(size, (0, 0, 255)),
            2: draw_token(size, (255, 150, 150)),
            3: draw_token(size, (150, 150, 255)),
        }


# --------------------------------------------- Helper Functions-------------------------------------------------

def draw_token(size, color):
    r = int(size // 2)
    s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)

    # Licht-/Materialparameter (einfaches PBR-ähnliches Approximation)
    # Licht kommt leicht von oben (z) und minimal von oben-mitte (y negative)
    Lx, Ly, Lz = 0.0, -0.25, 0.97
    # normalize L
    llen = (Lx * Lx + Ly * Ly + Lz * Lz) ** 0.5
    Lx, Ly, Lz = Lx / llen, Ly / llen, Lz / llen
    Vx, Vy, Vz = 0.0, 0.0, 1.0  # Blickrichtung zum Betrachter
    Hx, Hy, Hz = (Lx + Vx), (Ly + Vy), (Lz + Vz)
    hlen = (Hx * Hx + Hy * Hy + Hz * Hz) ** 0.5
    Hx, Hy, Hz = Hx / hlen, Hy / hlen, Hz / hlen

    ambient = 0.15
    kd = 0.8  # diffuse
    ks = 0.9  # specular intensity
    shininess = 80  # schärfe des Glanzes

    # Zeichne konzentrische Ringe von außen nach innen
    for i in range(r, 0, -1):
        d = i / r  # 1.0 am Rand, 0.0 in der Mitte
        # Normalkomponente der Halbkugel auf diesem Ring (N_z = sqrt(1 - d^2))
        nz = (1.0 - min(1.0, d * d)) ** 0.5

        # Einfache Beleuchtungsapproximation (N angenommen als (0,0,nz))
        NdotL = max(0.0, nz * Lz)
        diffuse_factor = ambient + kd * NdotL
        spec_factor = ks * (max(0.0, nz * Hz) ** shininess)

        # Farbe berechnen (Basisfarbe * diffuse + weißes Specular)
        col = [0, 0, 0]
        for j in range(3):
            diffuse_c = color[j] * diffuse_factor
            spec_c = 255 * spec_factor
            c = int(min(255, diffuse_c + spec_c))
            col[j] = c

        # Alpha: die Mitte ist etwas transparenter/heller im Glas-Look
        alpha = int(220 * (0.5 + 0.5 * nz))
        alpha = max(40, min(255, alpha))

        pygame.draw.circle(s, (*col, alpha), (r, r), i)

    # Highöights
    hx = int(r * 0.7)
    hy = int(r * 0.3)
    highlight = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    rect = (int(r - hx * 0.5), int(r - hy * 2), hx, hy)
    pygame.draw.ellipse(highlight, (255, 255, 255, 120), rect)
    s.blit(highlight, (0, 0), special_flags=0)

    return s


# -------------------------------------------- Draw Ring -------------------------------------------------

import math


def draw_ring(size, color):
    diameter = max(4, int(size))
    R = diameter // 2
    # innerer Radius als Anteil der äußeren Größe (Ringdicke)
    inner_ratio = 0.45
    r_inner = max(1, int(R * inner_ratio))

    s = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    cx, cy = R, R

    # Beleuchtungsparameter (wie in draw_token)
    Lx, Ly, Lz = 0.0, -0.25, 0.97
    llen = math.hypot(Lx, Ly, Lz)
    Lx, Ly, Lz = Lx / llen, Ly / llen, Lz / llen
    Vx, Vy, Vz = 0.0, 0.0, 1.0
    Hx, Hy, Hz = (Lx + Vx), (Ly + Vy), (Lz + Vz)
    hlen = math.hypot(Hx, Hy, Hz)
    Hx, Hy, Hz = Hx / hlen, Hy / hlen, Hz / hlen

    ambient = 0.12
    kd = 0.75
    ks = 0.9
    shininess = 80

    thickness = max(1, R - r_inner)
    # Zeichne konzentrische Ringe von außen nach innen (nur im Ringbereich)
    for i in range(R, r_inner, -1):
        # normierter Abstand über die Ringdicke (0=inner, 1=outer)
        x = (i - r_inner) / max(1.0, thickness)
        # approximierte Normalen-z Komponente über Profil (Mitte stärker gekrümmt)
        nx = 2.0 * (x - 0.5)
        nz = math.sqrt(max(0.0, 1.0 - min(1.0, nx * nx)))
        NdotL = max(0.0, nz * Lz)
        diffuse_factor = ambient + kd * NdotL
        spec_factor = ks * (max(0.0, nz * Hz) ** shininess)

        col = []
        for j in range(3):
            diffuse_c = color[j] * diffuse_factor
            spec_c = 255 * spec_factor
            c = int(min(255, diffuse_c + spec_c))
            col.append(c)

        # Alpha: außen stärker, innen etwas transparenter (Glaswirkung)
        alpha = int(200 * (0.6 + 0.4 * nz))
        alpha = max(30, min(255, alpha))

        pygame.draw.circle(s, (*col, alpha), (cx, cy), i)

    # Loch in der Mitte: vollständig transparent zeichnen
    pygame.draw.circle(s, (0, 0, 0, 0), (cx, cy), r_inner)

    # Kleiner innerer Glanz (Blendfläche) um den 3D-Effekt zu verstärken
    hx = int(R * 0.5)
    hy = int(R * 0.25)
    highlight = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    rect = (int(cx - hx * 0.6), int(cy - hy * 1.8), hx, hy)
    pygame.draw.ellipse(highlight, (255, 255, 255, 110), rect)
    s.blit(highlight, (0, 0), special_flags=0)

    # Außenreflex (schmaler hellerer Rand) für Glas-Silhouette
    edge = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(edge, (255, 255, 255, 30), (cx, cy), R, width=2)
    s.blit(edge, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return s


# -------------------------------------------- Draw cross -------------------------------------------------


def draw_cross(size, color):
    import pygame
    import math

    diameter = max(6, int(size))
    R = diameter // 2
    s = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    cx, cy = R, R

    # Beleuchtungsparameter (wie in draw_token/draw_ring)
    Lx, Ly, Lz = 0.0, -0.25, 0.97
    llen = math.hypot(Lx, Ly, Lz)
    Lx, Ly, Lz = Lx / llen, Ly / llen, Lz / llen
    Vx, Vy, Vz = 0.0, 0.0, 1.0
    Hx, Hy, Hz = (Lx + Vx), (Ly + Vy), (Lz + Vz)
    hlen = math.hypot(Hx, Hy, Hz)
    Hx, Hy, Hz = Hx / hlen, Hy / hlen, Hz / hlen

    ambient = 0.12
    kd = 0.75
    ks = 0.9
    shininess = 80

    # Balkenstärke (max/min) als Anteil des Radius
    max_thickness = max(2, int(R * 0.28))
    min_thickness = max(1, int(max_thickness * 0.35))

    # Linienenden leicht einziehen, damit das X innerhalb des Kreises sitzt
    margin = int(R * 0.9)
    a1 = (cx - margin, cy - margin)
    a2 = (cx + margin, cy + margin)
    b1 = (cx - margin, cy + margin)
    b2 = (cx + margin, cy - margin)

    # Zeichne mehrere Striche von außen nach innen, um Glas-Verlauf zu simulieren
    for w in range(max_thickness, min_thickness, -1):
        x = (w - min_thickness) / max(1.0, (max_thickness - min_thickness))
        nx = 2.0 * (x - 0.5)
        nz = math.sqrt(max(0.0, 1.0 - min(1.0, nx * nx)))
        NdotL = max(0.0, nz * Lz)
        diffuse_factor = ambient + kd * NdotL
        spec_factor = ks * (max(0.0, nz * Hz) ** shininess)

        col = []
        for j in range(3):
            diffuse_c = color[j] * diffuse_factor
            spec_c = 255 * spec_factor
            c = int(min(255, diffuse_c + spec_c))
            col.append(c)

        alpha = int(200 * (0.55 + 0.45 * nz))
        alpha = max(30, min(255, alpha))

        # Diagonalen zeichnen (mit abgerundeten Enden durch zusätzliche Kreise)
        pygame.draw.line(s, (*col, alpha), a1, a2, w)
        pygame.draw.circle(s, (*col, alpha), a1, max(1, w // 2))
        pygame.draw.circle(s, (*col, alpha), a2, max(1, w // 2))

        pygame.draw.line(s, (*col, alpha), b1, b2, w)
        pygame.draw.circle(s, (*col, alpha), b1, max(1, w // 2))
        pygame.draw.circle(s, (*col, alpha), b2, max(1, w // 2))

    # Kleiner innerer Soft-Hole-Effekt (optional, leichte Transparenz in Mitte)
    inner_soft = max(1, int(R * 0.15))
    center_mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(center_mask, (0, 0, 0, 0), (cx, cy), inner_soft)
    s.blit(center_mask, (0, 0))

    # Highlight entlang einer Diagonale für Glas-Effekt
    highlight = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    hl_w = max(1, int(R * 0.08))
    # leichte Verschiebung um Eindruck von Licht zu geben
    pygame.draw.line(highlight, (255, 255, 255, 120), (cx - margin // 2, cy - margin // 2 - int(R * 0.08)),
                     (cx + margin // 2, cy + margin // 2 - int(R * 0.08)), hl_w)
    s.blit(highlight, (0, 0), special_flags=0)

    # Subtiles Außenlicht (Randaufhellung)
    edge = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(edge, (255, 255, 255, 30), (cx, cy), R, width=2)
    s.blit(edge, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return s
