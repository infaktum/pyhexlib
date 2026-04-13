from pyhex.grid import TokenGridLayer



# ------------------------------- GameBoard -----------------------------------

class GameBoard(TokenGridLayer):

    def __init__(self, assets):
        super().__init__()
        self.assets = assets
        self.marker = None
    def get(self, rc):
        return self.hexagons.get_token(rc, None)

    def remove(self,rc):
        del self.hexagons[rc]

    def put_marker(self, rc):
        self.marker = rc

    def remove_marker(self):
        self.marker = None

    def check_game_over(self, score,player):
        if score[player] < 1:
            print(f"Player {1 - player} wins!")

    def compute_score(self):
        score = [0, 0]
        for h in self.hexagons:
            piece = self.get_token(h)
            if piece == 0:
                score[0] += 1
            elif piece == 1:
                score[1] += 1

        return score

