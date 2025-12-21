from __future__ import annotations
import datetime as dt
import pandas as pd # type: ignore
from copy import deepcopy

ELO_DIFF_SCALING = 400.0
ELO_K = 20.0
ELO_K_NEWBIE_ADD = 50.0
ELO_K_NEWBIE_SCALE = 2.0
EMA_MIN_GAIN = 50.0
EMA_MAX_GAIN = 500.0
EMA_MIN_GAMES_PER_MONTH = 4

class Round:
    def __init__(self, winner: str|None, discarder: str|None, hand_points: int, penalties: dict[str, int]|None = None):
        self.winner = winner
        self.discarder = discarder
        self.hand_points = hand_points
        if penalties is None:
            self.penalties = {}
        self.penalties = deepcopy(penalties)
    
    def to_dict(self) -> dict:
        return {
            "winner": self.winner,
            "discarder": self.discarder,
            "hand_points": self.hand_points,
            "penalties": self.penalties
        }

    @classmethod
    def from_dict(cls, data: dict) -> Round:
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
        self.players = deepcopy(players)
        self.end_points = deepcopy(end_points)
        self.date = date
        if rounds is None:
            rounds = []
        self.rounds = deepcopy(rounds)

    def update_rounds(self, rounds: list[Round]) -> tuple[int, str]:
        """
        Only add the rounds if they are not already present
        """
        if len(self.rounds) == 0:
            self.rounds = deepcopy(rounds)
            return (0, "")
        return (1, "Rounds deja presents")

    def __eq__(self, other: Game) -> bool:
        if not(isinstance(other, Game)):
            return NotImplemented
        return (
            self.players == other.players and
            self.end_points == other.end_points and
            self.date == other.date
        )
    
    def __lt__(self, other: Game) -> bool:
        if not(isinstance(other, Game)):
            return NotImplemented
        return (
            (self.date, self.players, self.end_points) <
            (other.date, other.players, other.end_points)
        )
    
    def to_dict(self) -> dict:
        return {
            "players": self.players,
            "end_points": self.end_points,
            "date": self.date.isoformat(),
            "rounds": [r.to_dict() for r in self.rounds]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Game:
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

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __lt__(self, other: str|Player) -> bool:
        if isinstance(other, str):
            return self.name < other
        elif isinstance(other, Player):
            return self.name < other.name
        return NotImplemented
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'base_elo': self.base_elo
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Player:
        return Player(
            name = data['name'],
            base_elo = data['base_elo']
        )

class Data:
    def __init__(self, games: list[Game] = [], players: list[Player] = [], aliases: dict[str, str] = {}):
        self.games = deepcopy(games)
        self.players = deepcopy(players)
        self.aliases = deepcopy(aliases)
        self.name_to_player_id = {}
        for i in range(len(players)):
            self.name_to_player_id[players[i].name] = i
        self._update_ema()
    
    def add_game(self, game: Game) -> tuple[int, str]:
        for igame in range(len(self.games)):
            g = self.games[igame]
            if (self._calc_aliases(g.players), g.end_points, g.date) == (self._calc_aliases(game.players), game.end_points, game.date): # Parties egales aux alias pres
                err_code, err_mess = self.games[igame].update_rounds(game.rounds)
                if err_code == 0:
                    return (1, "Partie en double (Rounds ajoutes)")
                else:
                    return (1, "Partie en double")

        for i in range(len(game.players)):
            if not(game.players[i] in self.aliases):
                return (2, "Joueur inconnu")

        if sum(game.end_points) != 0:
            return (3, "Somme non nulle")
        
        if len(game.rounds) != 0 and len(game.rounds) < 9:
            return (4, "Ouest non atteint")
        
        self.games.append(game)
        self._update_ema()
        return (0, "")

    def add_player(self, player: Player) -> tuple[int, str]:
        if player in self.players:
            return (1, "Joueur deja present")
        if player in self.aliases:
            return (2, "Alias deja present")

        self.players.append(player)
        self.aliases[player.name] = player.name
        self.name_to_player_id[player.name] = len(self.players) - 1
        self._update_ema()
        return (0, "")

    def add_alias(self, alias: str, player_name: str) -> tuple[int, str]:
        if alias in self.aliases:
            return (1, "Alias deja present")
        if not(player_name in self.players):
            return (2, "Joueur non present")

        self.aliases[alias] = player_name
        return (0, "")
    
    def remove_player(self, player_name: str) -> tuple[int, str]:
        if not(player_name) in self.players:
            return (1, "Joueur inexistant")
        
        games_to_remove = []
        for igame in range(len(self.games)):
            if player_name in self.games[igame].players:
                games_to_remove.append(igame)
        aliases_to_remove = []
        for alias in self.aliases.keys():
            if self.aliases[alias] == player_name:
                aliases_to_remove.append(alias)
        self.remove_games(games_to_remove)
        self.remove_aliases(aliases_to_remove)
        player_id = 0
        while self.players[player_id].name != player_name:
            player_id += 1
        self.players.pop(player_id)
        return (0, "")

    def remove_games(self, game_ids: list[int]):
        game_ids.append(len(self.games) + 10)
        new_games = []
        remove_id = 0
        for id in range(len(self.games)):
            if id == game_ids[remove_id]:
                remove_id += 1
            else:
                new_games.append(self.games[id])
        game_ids.pop()
        self.games = new_games

    def remove_aliases(self, aliases: list[str]):
        for alias in aliases:
            self.aliases.pop(alias, None)

    def _update_elo(self):
        """
        Format de 'elo' et 'nb_games' : tab[num game][player name]
        """
        self.games = sorted(self.games)
        self.players = sorted(self.players)
        current_elo = {}
        current_nb_games = {}
        for p in self.players:
            current_elo[p.name] = p.base_elo
            current_nb_games[p.name] = 0
        self.elo = []
        self.nb_games = []

        for game in self.games:
            rank_points = pd.Series(game.end_points).rank()
            game_points = {}
            for i in range(len(game.players)):
                game_points[game.players[i]] = float(rank_points[i]) - 1
            
            expected_points = {}
            for alias1 in game.players:
                expected_points[alias1] = 0.0
                for alias2 in game.players:
                    if alias1 != alias2:
                        name1 = self.aliases[alias1]
                        name2 = self.aliases[alias2]
                        expected_points[alias1] += 1.0 / (1.0 + 10 ** ((current_elo[name2] - current_elo[name1]) / ELO_DIFF_SCALING))
            
            elo_gain = {}
            for alias in game.players:
                name = self.aliases[alias]
                coef = ELO_K + ELO_K_NEWBIE_ADD / (ELO_K_NEWBIE_SCALE + current_nb_games[name])
                elo_gain[alias] = coef * (game_points[alias] - expected_points[alias])
            
            for alias in game.players:
                name = self.aliases[alias]
                current_elo[name] += elo_gain[alias]
                current_nb_games[name] += 1
            self.elo.append(deepcopy(current_elo))
            self.nb_games.append(deepcopy(current_nb_games))

    def _update_ema(self):
        """
        Format de 'ema' : tab[month](num_month, {joueur: stats_ema})
        Stats for EMA : elo, nb games, ema gain, total ema, rank
        """
        self._update_elo()
        last_nb_games = {}
        current_ema_stats = {}
        for p in self.players:
            last_nb_games[p.name] = 0
            current_ema_stats[p.name] = {
                'elo': p.base_elo,
                'nb games': 0,
                'ema gain': 0,
                'total ema': 0,
                'rank': -1
            }
        self.ema = []

        for igame in range(len(self.games)):
            if igame == len(self.games)-1 or self._get_num_month(igame) != self._get_num_month(igame+1):
                num_month = self._get_num_month(igame)
                for p in self.players:
                    current_ema_stats[p.name]['elo'] = self.elo[igame][p.name]
                    current_ema_stats[p.name]['nb games'] = self.nb_games[igame][p.name] - last_nb_games[p.name]
                    last_nb_games[p.name] = self.nb_games[igame][p.name]

                list_elos = []
                for p in self.players:
                    if current_ema_stats[p.name]['nb games'] > 0:
                        list_elos.append((current_ema_stats[p.name]['elo'], p.name))
                    else:
                        current_ema_stats[p.name]['rank'] = -1
                list_elos.sort()
                for pos in range(len(list_elos)):
                    name = list_elos[pos][1]
                    current_ema_stats[name]['rank'] = len(list_elos) - pos
                
                for p in self.players:
                    rank = current_ema_stats[p.name]['rank']
                    pos = len(list_elos) - rank
                    nb_games = current_ema_stats[p.name]['nb games']
                    current_ema_stats[p.name]['ema gain'] = (min(nb_games, EMA_MIN_GAMES_PER_MONTH) / EMA_MIN_GAMES_PER_MONTH) * (EMA_MIN_GAIN + (EMA_MAX_GAIN - EMA_MIN_GAIN) * (pos / (len(list_elos) - 1)))
                    current_ema_stats[p.name]['total ema'] = current_ema_stats[p.name]['total ema'] + current_ema_stats[p.name]['ema gain']
                
                self.ema.append((num_month, deepcopy(current_ema_stats)))

    def _get_readable_elo_dict(self) -> dict:
        current_elo = {}
        for p in self.players:
            current_elo[p.name] = p.base_elo
        elo_dict = {}
        for igame in range(len(self.games)):
            game = self.games[igame]
            datestr = game.date.isoformat()
            elo_dict[datestr] = {"elo": self.elo[igame]}
            elo_dict[datestr]['elo_before'] = {}
            elo_dict[datestr]['elo_diff'] = {}
            elo_dict[datestr]['points'] = {}
            elo_dict[datestr]['awaited_perf'] = {}
            elo_dict[datestr]['elo_gain'] = {}
            for iplayer in range(len(game.players)):
                name = self.aliases[game.players[iplayer]]
                elo_dict[datestr]['elo_gain'][name] = self.elo[igame][name] - current_elo[name]
                elo_dict[datestr]['points'][name] = sorted(game.end_points).index(game.end_points[iplayer])
                elo_dict[datestr]['elo_before'][name] = current_elo[name]
                elo_dict[datestr]['awaited_perf'][name] = 0.0
                mean_elo = 0
                for alias2 in game.players:
                    name2 = self.aliases[alias2]
                    if name != name2:
                        elo_dict[datestr]['awaited_perf'][name] += 1.0 / (1.0 + 10 ** ((current_elo[name2] - current_elo[name]) / ELO_DIFF_SCALING))
                        mean_elo += current_elo[name2]
                mean_elo /= len(game.players) - 1
                elo_dict[datestr]['elo_diff'][name] = current_elo[name] - mean_elo
            current_elo = self.elo[igame]
        return elo_dict

    def _get_num_month(self, igame: int) -> int:
        """ Returns the number of the month with year included """
        game = self.games[igame]
        return game.date.year * 12 + game.date.month
    
    def _calc_aliases(self, names: list[str]) -> list[str]:
        new_names = []
        for name in names:
            new_names.append(self.aliases[name])
        return new_names

    def to_dict(self) -> dict:
        return {
            'games': [g.to_dict() for g in self.games],
            'players': [p.to_dict() for p in self.players],
            'aliases': self.aliases
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Data:
        return Data(
            games = [Game.from_dict(g) for g in data['games']],
            players = [Player.from_dict(p) for p in data['players']],
            aliases = data['aliases']
        )