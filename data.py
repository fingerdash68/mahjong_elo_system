class Round:
    def __init__(self, winner: str, discarder: str, penalties: dict[str, int] | None):
        self.winner = winner
        self.discarder = discarder
        if penalties is None:
            penalties = {}
        self.penalties = penalties
    
    def to_dict(self) -> dict:
        return {
            "winner": self.winner,
            "discarder": self.discarder,
            "penalties": self.penalties
        }

class Game:
    