"""Rules for the two-player hex token game."""

from pyhexlib.tokens import SimpleToken


class Game:
    def __init__(self, token_layer, assets, hexagons):
        self.token_layer = token_layer
        self.assets = assets
        self.hexagons = hexagons
        self.marker = None

    def setup(self, pos0, pos1):
        if pos0 not in self.hexagons or pos1 not in self.hexagons or pos0 == pos1:
            raise ValueError("Starting positions must be distinct board fields")
        self.token_layer.clear()
        self.put_piece(pos0, 0)
        self.put_piece(pos1, 1)

    def get_token(self, rc):
        return self.token_layer.get_token(rc)

    def get_piece(self, rc):
        return self.token_layer.get_token_id(rc)

    def put_piece(self, rc, player):
        if rc not in self.hexagons or player not in (0, 1):
            raise ValueError("Invalid field or player")
        self.token_layer.set_token(rc, SimpleToken(player, self.assets.get_image(player), rc=rc))

    def remove_piece(self, rc):
        self.token_layer.remove_token(rc)

    def put_marker(self, rc):
        self.marker = rc

    def remove_marker(self):
        self.marker = None

    def positions(self):
        return {rc: self.get_piece(rc) for rc in self.token_layer.hexagons}

    def legal_moves(self, player, positions=None):
        positions = self.positions() if positions is None else positions
        moves = []
        for source in positions:
            if positions[source] != player:
                continue
            for target in self.hexagons.neighbors(source, dist=2):
                if target not in positions:
                    moves.append((source, target))
        return moves

    def legal_targets(self, source, player):
        if self.get_piece(source) != player:
            return []
        return [target for target in self.hexagons.neighbors(source, dist=2)
                if self.get_piece(target) is None]

    def apply_move(self, source, target, player):
        if target not in self.legal_targets(source, player):
            raise ValueError("Illegal move")
        distance = self.hexagons.get_distance(source, target)
        if distance == 2:
            self.remove_piece(source)
        self.put_piece(target, player)
        for neighbor in self.hexagons.neighbors(target):
            if self.get_piece(neighbor) == 1 - player:
                self.put_piece(neighbor, player)

    def compute_score(self):
        positions = self.positions()
        return [sum(owner == player for owner in positions.values()) for player in (0, 1)]

    def is_game_over(self):
        score = self.compute_score()
        return (0 in score or len(self.token_layer.hexagons) == len(self.hexagons)
                or (not self.legal_moves(0) and not self.legal_moves(1)))

    def winner(self):
        if not self.is_game_over():
            return None
        red, blue = self.compute_score()
        return 0 if red > blue else 1 if blue > red else -1

    def best_move(self, player):
        """Choose the move with the best immediate material gain."""
        positions = self.positions()
        moves = self.legal_moves(player, positions)
        if not moves:
            return None

        def value(move):
            source, target = move
            flips = sum(positions.get(n) == 1 - player for n in self.hexagons.neighbors(target))
            clone = self.hexagons.get_distance(source, target) == 1
            return (2 * flips + int(clone), int(clone))

        return max(sorted(moves), key=value)
