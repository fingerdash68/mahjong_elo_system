import datetime as dt

class Round:
    def __init__(self, *, winner: str|None = None, discarder: str|None = None, hand_points: int, penalties: dict[str, int]|None = None, data_dict: dict|None = None):
        if data_dict is None:
            self.winner = winner
            self.discarder = discarder
            self.hand_points = hand_points
            if penalties is None:
                penalties = {}
            self.penalties = penalties
        else:
            self.from_dict(data_dict)
    
    def to_dict(self) -> dict:
        return {
            "winner": self.winner,
            "discarder": self.discarder,
            "hand_points": self.hand_points,
            "penalties": self.penalties
        }

    def from_dict(self, data: dict):
        self.winner = data['winner']
        self.discarder = data['discarder']
        self.hand_points = data['hand_points']
        self.penalties = data['penalties']

    def __str__(self):
        return f"winner={self.winner}, discarder={self.discarder}, points={self.hand_points}, penalties={self.penalties}"

class Game:
    def __init__(self, players: list[str], end_points: list[int], date: dt.datetime, rounds: list[Round]|None = None):
        self.players = players
        self.end_points = end_points
        self.date = date
        self.rounds = rounds
    
    def to_dict(self) -> dict:
        return {
            "players": self.players,
            "end_points": self.end_points,
            "date": self.date,
            "rounds": self.rounds
        }
    
    def from_dict(self, data: dict):
        self.players = data['players']
        self.end_points = data['end_points']
        self.date = data['date']
        self.rounds = data['rounds']

class Player:
    def __init__(self, name: str, base_elo: float):
        self.name = name
        self.base_elo = base_elo
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'base_elo': self.base_elo
        }
    
    def from_dict(self, data: dict):
        self.name = data['name']
        self.base_elo = data['base_elo']

class Data:
    def __init__(self, games: list[Game] = [], players: list[Player] = []):
        self.games = games
        self.players = players
    
    def add_game(self, game: Game):
        self.games.append(game)

    def to_dict(self) -> dict:
        return {
            'games': self.games,
            'players': self.players
        }
    
    def from_dict(self, data: dict):
        self.games = data['games']
        self.players = data['players']