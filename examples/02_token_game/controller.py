"""Human input and computer turns for the token game."""

import pygame


COLORS = {0: (255, 100, 100), 1: (100, 100, 255)}


class Controller:
    def __init__(self, board, renderer, offset=(0, 0)):
        self.board = board
        self.renderer = renderer
        self.offset = offset
        self.outline = renderer.get_layer("outline")
        self.fields = renderer.get_layer("background")
        self.shadows = renderer.get_layer("shadows")
        self.valid_hexes = []
        self.player = 0  # Red is human, blue is the computer.
        self.state = "UPDATE"

    def score(self):
        return self.board.compute_score(), self.player

    def clear_selection(self):
        self.board.remove_marker()
        self.valid_hexes = []
        self.outline.clear()
        self.fields.clear()
        self.shadows.clear()
        self.state = "UPDATE"

    def select(self, rc):
        self.clear_selection()
        self.board.put_marker(rc)
        self.valid_hexes = self.board.legal_targets(rc, self.player)
        self.outline.set_style(rc, color=COLORS[self.player], width=4)
        self.fields.set_color(self.valid_hexes, (255, 200, 200))
        self.state = "UPDATE"

    def advance_turn(self):
        if self.board.is_game_over():
            return
        self.player = 1 - self.player
        if not self.board.legal_moves(self.player):
            self.player = 1 - self.player  # A player with no move passes.

    def play_ai_turn(self):
        while self.player == 1 and not self.board.is_game_over():
            move = self.board.best_move(1)
            if move is None:
                self.advance_turn()
                break
            self.board.apply_move(*move, player=1)
            self.advance_turn()
            self.state = "UPDATE"

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.player != 0 or self.board.is_game_over():
            return
        x, y = event.pos[0] - self.offset[0], event.pos[1] - self.offset[1]
        if x < 0 or y < 0 or x >= self.renderer.width or y >= self.renderer.height:
            return
        rc = self.renderer.hex_at(x, y)
        if rc == self.board.marker:
            self.clear_selection()
        elif self.board.get_piece(rc) == self.player:
            self.select(rc)
        elif rc in self.valid_hexes:
            self.board.apply_move(self.board.marker, rc, self.player)
            self.clear_selection()
            self.advance_turn()
            self.play_ai_turn()
