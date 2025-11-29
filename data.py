from __future__ import annotations
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
    def from_dict(self, data: dict) -> Round:
        return Round(
            winner = data['winner'],
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

    def __eq__(self, other: Game) -> bool:
        if not(isinstance(other, Game)):
            return NotImplemented
        return self.players == other.players and self.end_points == other.end_points and self.date == other.date
    
    def to_dict(self) -> dict:
        return {
            "players": self.players,
            "end_points": self.end_points,
            "date": self.date.isoformat(),
            "rounds": [r.to_dict() for r in self.rounds]
        }
    
    @classmethod
    def from_dict(self, data: dict) -> Game:
        return Game(
            players = data['players'],
            end_points = data['end_points'],
            date = dt.datetime.fromisoformat(data['date']),
            rounds = [Round.from_dict(r) for r in data['rounds']]
        )

class Player:
    def __init__(self, name: str, base_elo: float):
        self.name = name
        self.base_elo = base_elo

    def rename(self, new_name: str):
        self.name = new_name
    
    def __eq__(self, other: str|Player) -> bool:
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Player):
            return self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'base_elo': self.base_elo
        }
    
    @classmethod
    def from_dict(self, data: dict) -> Player:
        return Player(
            name = data['name'],
            base_elo = data['base_elo']
        )

class Data:
    def __init__(self, games: list[Game] = [], players: list[Player] = [], aliases: dict[str, str] = {}):
        self.games = games
        self.players = players
        self.aliases = aliases
        self.name_to_player_id = {}
        for i in range(len(players)):
            self.name_to_player_id[players[i].name] = i
    
    def add_game(self, game: Game) -> tuple[int, str]:
        if game in self.games:
            return (1, "Partie en double")

        for i in range(len(game.players)):
            if not(game.players[i] in self.aliases):
                return (2, "Joueur inconnu")

        if sum(game.end_points) != 0:
            return (3, "Somme non nulle")
        
        self.games.append(game)
        return (0, "")

    def add_player(self, player: Player) -> tuple[int, str]:
        if player in self.players:
            return (1, "Joueur deja present")
        if player in self.aliases:
            return (2, "Alias deja present")

        self.players.append(player)
        self.aliases[player.name] = player.name
        self.name_to_player_id[player.name] = len(self.players) - 1
        return (0, "")

    def add_alias(self, alias: str, player_name: str) -> tuple[int, str]:
        if alias in self.aliases:
            return (1, "Alias deja present")
        if not(player_name in self.players):
            return (2, "Joueur non present")

        self.aliases[alias] = player_name
        return (0, "")

    def to_dict(self) -> dict:
        return {
            'games': [g.to_dict() for g in self.games],
            'players': [p.to_dict() for p in self.players],
            'aliases': self.aliases
        }
    
    @classmethod
    def from_dict(self, data: dict) -> Data:
        return Data(
            games = [Game.from_dict(g) for g in data['games']],
            players = [Player.from_dict(p) for p in data['players']],
            aliases = data['aliases']
        )