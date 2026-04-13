import pygame

# --------------------------------- COLOR CONSTANTS -----------------------------------

COLOR = {0: {'light': (255, 200, 200), 'dark': (255, 150, 150)}, 1: {'light': (200, 200, 255), 'dark': (150, 150, 255)}}

COLORS_PLAYER_0 = {"marker": (255, 100, 100), "fields_light": (255, 200, 200), "fields_dark": (255, 150, 150)}
COLORS_PLAYER_1 = {"marker": (100, 100, 255), "fields_light": (200, 200, 255), "fields_dark": (150, 150, 255)}

COLORS_PLAYERS = {0: COLORS_PLAYER_0, 1: COLORS_PLAYER_1}


# ------------------------------ Controller -----------------------------------

class Controller:
    def __init__(self, board, renderer):
        self.grids = renderer.layers
        self.hexagons = renderer.layers.hexagons
        self.board = board
        self.outline = renderer.get_layer("outline")
        self.fields = renderer.get_layer("background")
        self.shadows = renderer.get_layer("shadows")

        self.renderer = renderer

        self.valid_hexes = []
        self.player = 1
        self.state = "IDLE"

    def put_shadow_token(self, rc, player):

        self.shadows.set_image(rc, self.renderer.assets.get_image(player + 2))  # shadow token

    def remove_shadow_token(self):
        self.shadows.clear()

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
            rc = self.renderer.hex_at(x, y)

            if not self.board.marker:

                if self.board.get_piece(rc) is not None and self.board.get_piece(rc) == self.player:
                    self.set_marker(rc)

                    self.valid_hexes = self.compute_valid_hexes()
                    self.fields.set_color(self.valid_hexes, COLORS_PLAYERS[self.player]["fields_light"])
                    self.state = "UPDATE"
            else:
                if rc == self.board.marker:
                    self.remove_marker()
                    self.fields.remove_all_colors()
                    self.state = "UPDATE"

                elif rc in self.valid_hexes:
                    self.handle_move(rc)
                    self.remove_marker()
                    self.fields.clear()

                    self.switch_player()
                    self.board.check_game_over(self.score()[0], self.player)
                    self.state = "UPDATE"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                self.renderer.layers.toggle_coordinate_layer()
                self.state = "UPDATE"

    # ------------------------------ Game Actions -------------------------------

    def compute_valid_hexes(self):
        neighbors = self.hexagons._neighbors_without_cost(self.board.marker, dist=2)
        valid_hexes = [h for h in neighbors if self.board.get_token(h) is None]
        return valid_hexes

    def switch_player(self):
        self.player = 1 - self.player

    def score(self):
        score = self.board.compute_score()
        return score, self.player

    def distance(self, h1, h2):
        return self.grids.hexagons.get_distance(h1, h2)

    def handle_move(self, rc):
        if self.distance(self.board.marker, rc) == 1:  # clone
            self.board.put_piece(rc, self.player)

        elif self.distance(self.board.marker, rc) == 2:  # jump
            self.board.remove_piece(self.board.marker)
            self.board.put_piece(rc, self.player)

        self.flip_neighbors(rc)

    def flip_neighbors(self, rc):
        for n in self.hexagons._neighbors_without_cost(rc):
            if self.board.get_token(n) is not None and self.board.get_token(n) != self.player:
                self.board.put_piece(n, self.player)

    def remove_marker(self):
        self.board.remove_marker()
        self.outline.clear()

    def set_marker(self, rc):
        self.board.put_marker(rc)
        self.outline.set_style(rc, color=COLORS_PLAYERS[self.player]["marker"], width=4)
