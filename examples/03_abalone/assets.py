import pygame

from pyhexlib.graphic import Assets


# -------------------------------------------- Assets -------------------------------------------------

class GameAssets(Assets):
    def __init__(self, size):
        self.tokens = {
            0: draw_token(size, (230, 230, 230)),
            1: draw_token(size, (30, 30, 30)),
            2: draw_token(size, (180, 180, 180)),
            3: draw_token(size, (80, 80, 80)),
        }


def draw_token(size, color):
    r = int(4 * size // 5)
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
