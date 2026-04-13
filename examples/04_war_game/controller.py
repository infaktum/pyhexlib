import pygame

from pyhex.utils import toggle_coordinate_layer, handle_scrolling_event

# ------------------------------ Constants -----------------------------------

COLOR_PATH = COLOR_MARKER = (100, 100, 255)
COLOR_HIGHLIGHT = (255, 255, 255, 50)


# ------------------------------ Controller -----------------------------------

class Controller:
    def __init__(self, board, renderer):
        self.hexagons = renderer.layers.hexagons
        self.board = board
        self.markers = renderer.get_layer("outline")
        self.fields = renderer.get_layer("background")
        self.movement = renderer.get_layer("terrain")
        self.moves = renderer.get_layer("neighbors")
        self.path_grid = renderer.get_layer("path")
        self.shadows = renderer.get_layer("shadows")
        self.path = None

        self.renderer = renderer
        self.current_rc = None
        self.active = None

        self.grid_key_mapping = {n + pygame.K_1: grid for n, grid in enumerate(renderer.layers.layers.keys())}

        self.valid_moves = []
        self.state = "IDLE"

    def put_shadow_token(self, rc, direction):
        shadow = self.board.shadow_tokens["tank"] if self.active.id == "tank" else self.board.shadow_tokens["plane"]
        shadow.direction = direction
        self.shadows.set_token(rc, shadow)

    def remove_shadow_token(self):
        self.shadows.clear()

    # ------------------------------ Event Handling -------------------------------

    def handle_event(self, event):
        self.state = "IDLE"

        if event.type == pygame.MOUSEMOTION:
            if self.board.marker:
                rc = self.renderer.hex_at(*event.pos)
                if rc != self.current_rc:
                    self.current_rc = rc
                    self.path_grid.remove_path()
                    self.remove_shadow_token()
                    if rc in self.valid_moves:
                        if self.board.get_token(rc) is None:
                            self.path = self.hexagons.path(self.board.marker, rc, cost_fn=self.movement.get_value)
                            direction = self.hexagons.get_direction(self.path[-2], rc)
                            self.put_shadow_token(rc, direction)
                            self.path = self.hexagons.path(self.board.marker, rc, cost_fn=self.movement.get_value)
                            self.path_grid.color = COLOR_PATH
                            self.path_grid.set_path(self.path)
                            self.board.set_token(self.board.marker, self.active,
                                                 self.hexagons.get_direction(self.board.marker, self.path[1]))
                    self.state = "UPDATE"

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            rc = self.renderer.hex_at(x, y)

            if self.board.marker is None:
                self.active = self.board.get_token(rc)
                print(self.active)
                if self.active is not None:
                    self.set_marker(rc)
                    movement_range = self.active.movement
                    self.valid_moves = self.find_valid_moves(range=movement_range, cost_fn=self.movement.get_value)
                    self.moves.set_color(self.valid_moves, COLOR_HIGHLIGHT)
                    self.state = "UPDATE"
            else:
                if rc == self.board.marker:
                    self.remove_marker(rc)
                    self.moves.clear()
                    self.path_grid.remove_path()
                    self.state = "UPDATE"

                elif rc in self.valid_moves:
                    self.handle_move(rc)
                    self.remove_marker(self.board.marker)
                    self.moves.clear()
                    self.path_grid.remove_path()
                    self.board.compute_score()
                    self.state = "UPDATE"

        if handle_scrolling_event(event, self.renderer):
            self.state = "UPDATE"

        if event.type == pygame.KEYDOWN:
            key = event.key

            if key == pygame.K_c:
                toggle_coordinate_layer(self.renderer.layers, font_color=(255, 255, 255), font_size=16)
                self.state = "UPDATE"

            if key in self.grid_key_mapping.keys():
                self.renderer.toggle_visible(self.grid_key_mapping[key])
                self.state = "UPDATE"

            if key == pygame.K_b:
                self.renderer.toggle_bg_visible()
                self.state = "UPDATE"

    # ---------------------------- Game Actions -------------------------------

    def find_valid_moves(self, range=5, cost_fn=None):
        return self.hexagons.neighbors(self.board.marker, max_cost=range, cost_fn=cost_fn)

    def distance(self, h1, h2):
        return self.hexagons.get_distance(h1, h2)

    def handle_move(self, rc):
        self.board.remove_token(self.board.marker)
        direction = self.hexagons.get_direction(self.path[-2], rc)
        self.board.set_token(rc, self.active, direction)

    def remove_marker(self, rc):
        self.board.remove_marker()
        self.markers.remove_style(rc)

    def set_marker(self, rc):
        self.board.put_marker(rc)
        self.markers.set_style(rc, color=(200, 200, 255), width=6)
