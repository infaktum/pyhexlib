import pygame

from pyhex.utils import toggle_coordinate_layer, handle_scrolling_event

# ------------------------------ Constants -----------------------------------

COLOR_PATH = COLOR_MARKER = (100, 100, 255)
COLOR_HIGHLIGHT = (255, 255, 255, 50)


# ------------------------------ Controller -----------------------------------

class Controller:
    def __init__(self, game_board, renderer):
        self.board = game_board
        self.renderer = renderer
        self.hexagons = renderer.layers.hexagons
        self.markers = renderer.get_layer("outline")
        self.fields = renderer.get_layer("background")
        self.movement = renderer.get_layer("terrain")
        self.moves = renderer.get_layer("neighbors")
        self.shadows = renderer.get_layer("shadows")
        self.game_board = game_board
        self.path = None

        self.current_rc = None
        self.active = None
        self.valid_moves = []
        self.player = 1
        self.state = "IDLE"

        self.mapping = {n: grid for n, grid in enumerate(renderer.layers.layers.values())}

    def put_shadow_tokens(self):
        for rc in self.path[1:]:
            shadow = self.board.get_shadow_token(self.active.id)

            shadow.direction = self.hexagons.get_direction(self.path[self.path.index(rc) - 1], rc)
            self.shadows.set_token(rc, shadow)

    def remove_shadow_tokens(self):
        self.shadows.clear()

    def new_game(self):
        self.board.setup()
        self.state = "UPDATE"

    # ------------------------------ Event Handling -------------------------------

    def handle_event(self, event):
        self.state = "IDLE"

        if event.type == pygame.MOUSEMOTION:
            if self.board.marker:
                rc = self.renderer.hex_at(*event.pos)
                if rc != self.current_rc:
                    self.current_rc = rc
                    self.remove_shadow_tokens()
                    if rc in self.valid_moves:
                        if self.board.get_token(rc) is None:
                            self.path = self.hexagons.path(self.board.marker, rc, cost_fn=self.movement.get_value)
                            self.path = self.hexagons.path(self.board.marker, rc, cost_fn=self.movement.get_value)
                            self.put_shadow_tokens()

                    if self.board.get_token(rc) and self.board.get_token(rc) != self.active:
                        self.put_target(rc)
                    self.state = "UPDATE"

        if handle_scrolling_event(event, self.renderer):
            self.state = "UPDATE"

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            rc = self.renderer.hex_at(x, y)
            print(rc)
            if not self.board.marker:
                self.active = self.board.get_token(rc)
                if self.active is not None and self.board.is_player_token(self.active):  # only player tokens
                    self.set_marker(rc)
                    # print(f'Selected token: {self.active}')
                    movement_range = self.active.movement
                    self.valid_moves = self.find_valid_moves(movement_range=movement_range,
                                                             cost_fn=self.movement.get_value)
                    self.moves.set_color(self.valid_moves, COLOR_HIGHLIGHT)
                    self.state = "UPDATE"
            else:
                if rc == self.board.marker:  # cancel move
                    self.remove_marker(rc)
                    self.moves.clear()
                    self.state = "UPDATE"

                elif rc in self.valid_moves:  # make move
                    self.handle_move(rc)
                    self.state = "UPDATE"

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_c:
                toggle_coordinate_layer(self.renderer.layers, font_color=(255, 255, 255), font_size=20)
                self.state = "UPDATE"

            elif event.key == pygame.K_b:
                self.toggle_background()
                self.state = "UPDATE"

            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                self.toggle_grid(event.key - pygame.K_1)
                self.state = "UPDATE"

    # ---------------------------- Renderer Actions -------------------------------

    def toggle_grid(self, number):
        if number in self.mapping.keys():
            self.mapping[number].visible = not self.mapping[number].visible

    def toggle_background(self):
        self.renderer.background_visible = not self.renderer.background_visible

    # ---------------------------- Game Actions -------------------------------

    def find_valid_moves(self, movement_range=5, cost_fn=None):
        neighbors = self.hexagons.neighbors(self.board.marker, max_cost=movement_range, cost_fn=cost_fn)
        return [rc for rc in neighbors if self.board.get_token(rc) is None]

    def distance(self, h1, h2):
        return self.hexagons.get_distance(h1, h2)

    def handle_move(self, rc):
        self.board.remove_token(self.board.marker)
        self.remove_marker(self.board.marker)
        self.remove_shadow_tokens()
        self.moves.clear()
        direction = self.hexagons.get_direction(self.path[-2], rc)
        self.board.set_token(rc, self.active, direction)
        self.board.turn_turrets(rc)

    def remove_marker(self, rc):
        self.board.remove_marker()
        self.markers.remove_style(rc)

    def set_marker(self, rc):
        self.board.put_marker(rc)
        self.markers.set_style(rc, color=COLOR_MARKER, width=6)

    def put_target(self, rc):
        self.board.put_target(rc)
