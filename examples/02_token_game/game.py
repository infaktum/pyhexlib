from pyhexlib.tokens import SimpleToken


# ------------------------------- GameBoard -----------------------------------


class Game:

    def __init__(self, token_layer, assets):
        self.token_layer = token_layer
        self.assets = assets

        self.player0 = SimpleToken(0, self.assets.get_image(0))
        self.player1 = SimpleToken(1, self.assets.get_image(1))

        self.marker = None

    def setup(self, pos0, pos1):
        self.put_piece(pos0, 0)
        self.put_piece(pos1, 1)

    def set_token(self, rc, token):
        self.token_layer.set_token(rc, token)
        token.rc = rc

    def get_token(self, rc):
        return self.token_layer.get_image(rc)

    def put_piece(self, rc, player: int):
        token = SimpleToken(player, self.assets.get_image(player))
        self.set_token(rc, token)

    def remove_piece(self, rc):
        self.token_layer.remove_token(rc)

    def get_piece(self, rc) -> int:
        return self.token_layer.get_token_id(rc)

    def put_marker(self, rc):
        self.marker = rc

    def remove_marker(self):
        self.marker = None

    def check_game_over(self, score, player):
        if score[player] < 1:
            print(f"Player {1 - player} wins!")

    def compute_score(self):
        score = [0, 0]
        for h in self.token_layer.hexagons:
            piece = self.get_piece(h)
            if piece == 0:
                score[0] += 1
            elif piece == 1:
                score[1] += 1
        return score
