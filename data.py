import datetime as dt

class Round:
    def __init__(self, winner: str|None, discarder: str|None, hand_points: int, penalties: dict[str, int]|None = {}):
        self.winner = winner
        self.discarder = discarder
        self.hand_points = hand_points
        self.penalties = penalties
    
    def to_dict(self) -> dict:
        return {
            "winner": self.winner,
            "discarder": self.discarder,
            "hand_points": self.hand_points,
            "penalties": self.penalties
        }

    @classmethod
    def from_dict(self, data: dict) -> "Round":
        return Round(winner = data['winner'],
            discarder = data['discarder'],
            hand_points = data['hand_points'],
            penalties = data['penalties']
        )

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
            "date": self.date.isoformat(),
            "rounds": [r.to_dict() for r in self.rounds]
        }
    
    @classmethod
    def from_dict(self, data: dict) -> "Game":
        return Game(players = data['players'],
            end_points = data['end_points'],
            date = dt.datetime.fromisoformat(data['date']),
            rounds = [data['rounds']]
        )

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