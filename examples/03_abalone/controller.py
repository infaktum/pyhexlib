import pygame

# ------------------------------ Constants -----------------------------------

COLORS_PLAYER_0 = {"marker": (200, 200, 200), "fields_light": (220, 220, 220)}
COLORS_PLAYER_1 = {"marker": (50, 50, 50), "fields_light": (80, 80, 80)}

COLORS_PLAYERS = {0: COLORS_PLAYER_0, 1: COLORS_PLAYER_1}


# ------------------------------ Controller -----------------------------------

class Controller:
    def __init__(self, renderer):
        self.grids = renderer.layers
        self.hexagons = renderer.layers.hexagons
        self.board = renderer.get_layer("game")
        self.outline = renderer.get_layer("outline")
        self.fields = renderer.get_layer("background")
        self.shadows = renderer.get_layer("shadows")

        self.renderer = renderer

        self.valid_hexes = []
        self.player = 1
        self.state = "IDLE"

    def put_shadow_token(self, rc, player):
        self.shadows.set_image(rc, self.renderer.assets.get_token(player + 2))  # shadow token

    def remove_shadow_token(self):
        self.shadows.remove_all_images()

    # ------------------------------ Event Handling -------------------------------

    def handle_event(self, event):
        self.state = "IDLE"

        if event.type == pygame.MOUSEMOTION:
            if self.board.marker:
                rc = self.renderer.hex_at(*event.pos)
                self.remove_shadow_token()
                if rc in self.valid_hexes:
                    if self.board.get_token(rc) is None:
                        self.put_shadow_token(rc, self.player)  # preview token
                self.state = "UPDATE"

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            hex = self.renderer.hex_at(x, y)
            print(x, y, hex)
            if not self.board.marker:
                if self.board.get_token(hex) is not None and self.board.get_token(hex) == self.player:
                    self.set_marker(hex)

                    self.valid_hexes = self.compute_valid_hexes()
                    self.fields.set_color(self.valid_hexes, COLORS_PLAYERS[self.player]["fields_light"])
                    self.state = "UPDATE"
            else:
                if hex == self.board.marker:
                    self.remove_marker(hex)
                    self.fields.remove_all_colors()
                    self.state = "UPDATE"

                elif hex in self.valid_hexes:
                    self.handle_move(hex)
                    self.remove_marker(self.board.marker)
                    self.fields.remove_all_colors()

                    self.switch_player()
                    self.board.check_game_over(self.score()[0], self.player)
                    self.state = "UPDATE"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.grids.toggle_coordinate_layer()
                self.state = "UPDATE"

    # ------------------------------ Game Actions -------------------------------

    def compute_valid_hexes(self):
        neighbors = near_hexagons(self.hexagons, self.board.marker, dist=2)
        valid_hexes = [h for h in neighbors if self.board.get_token(h) is None]
        return valid_hexes

    def switch_player(self):
        self.player = 1 - self.player

    def score(self):
        score = self.board.compute_score()
        return score, self.player

    def distance(self, h1, h2):
        return self.grids.distance_axial(h1, h2)

    def handle_move(self, rc):
        pass

    def remove_marker(self, rc):
        self.board.remove_marker()
        self.outline.remove_all_styles()

    def set_marker(self, rc):
        self.board.put_marker(rc)
        self.outline.set_style(rc, color=COLORS_PLAYERS[self.player]["marker"], width=4)

# ------------------------------ End Controller -------------------------------
