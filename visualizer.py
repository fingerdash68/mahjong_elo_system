import matplotlib.pyplot as plt
from data import *
import os
from pprint import pprint
from statistics import mean
from typing import Any

class Visualizer:
    def __init__(self, data: Data):
        self.data = data
    
    def plot_elos(self, players_per_plot: int = 4, save_file: str = ""):
        # Extract shared time axis
        dates = [g.date for g in self.data.games]

        # All player names
        all_players = list(sorted(
            self.data.elo[0].keys(),
            key = lambda x : self.data.elo[-1][x], # Sort by elo
            reverse = True
        ))

        # Manual chunking
        def chunked(iterable, size):
            for i in range(0, len(iterable), size):
                yield iterable[i:i+size]

        # Prepare save mode
        save_mode = None
        if save_file != "":
            if save_file.endswith("/") or save_file.endswith("\\"):
                save_mode = "directory"
                os.makedirs(save_file, exist_ok=True)
            else:
                save_mode = "prefix"

        # Create a figure for each group of players
        fig_index = 1
        for group in chunked(all_players, players_per_plot):
            plt.figure(figsize=(10, 6))

            for player in group:
                elo_values = [elo[player] for elo in self.data.elo]

                # Remove duplicates of dates
                dates_no_dup = []
                elo_values_no_dup = []
                still_starting_elo = True
                for i in range(len(dates)):
                    if still_starting_elo and (i == len(dates) - 1 or elo_values[i+1] != elo_values[i]):
                        still_starting_elo = False
                        dates_no_dup.append(dates[i])
                        elo_values_no_dup.append(elo_values[i])
                    if not(still_starting_elo) and (i == len(dates) - 1 or (dates[i+1] - dates[i]).days >= 1):
                        dates_no_dup.append(dates[i])
                        elo_values_no_dup.append(elo_values[i])
                        
                plt.plot(dates_no_dup, elo_values_no_dup, label=player)
                # plt.plot(dates, elo_values, label=player)

            plt.xlabel("Date")
            plt.ylabel("Elo Rating")
            plt.title(f"Elo Progression — {', '.join(group)}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            # Save if needed
            if save_mode == "directory":
                out_path = os.path.join(save_file, f"elo_{"_".join(group)}.png")
                plt.savefig(out_path)
            elif save_mode == "prefix":
                out_path = f"{save_file}_{"_".join(group)}.png"
                plt.savefig(out_path)
            
            # Show only when not saving
            if save_file == "":
                plt.show()

            plt.close()
            fig_index += 1

    def plot_emas(self, save_file: str = ""):
        # Prepare save mode
        save_mode = None
        if save_file != "":
            if save_file.endswith("/") or save_file.endswith("\\"):
                save_mode = "directory"
                os.makedirs(save_file, exist_ok=True)
            else:
                save_mode = "prefix"

        # Prepare the table
        months_name = ['Jan', 'Fev', 'Mars', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout', 'Sept', 'Oct', 'Nov', 'Dec']
        for id_month, ema_stats in self.data.ema:
            month = (id_month - 1) % 12
            year = (id_month - 1) // 12
            date_name = months_name[month] + " " + str(year)

            ema_table = []
            for name, stats in ema_stats.items():
                if stats['rank'] != -1 or True: # Filter
                    ema_table.append([
                        name,
                        round(stats['elo'], 1),
                        stats['rank'],
                        stats['nb games'],
                        round(stats['ema gain']),
                        round(stats['total ema'])])
            ema_table.sort(
                key = lambda x : x[5], # Total EMA sorting
                reverse = True
            )
            ema_table.insert(0, [date_name, 'Elo', 'Rang', 'Nb parties', 'EMA mois', 'EMA total'])

            fig, ax = plt.subplots()
            ax.axis('off')
            fig.tight_layout()

            table = ax.table(
                cellText=ema_table,
                cellLoc='center',
                loc='center'
            )

            table.scale(1.0, 1.2)
            for i in range(len(ema_table[0])):
                table[(0, i)].set_text_props(weight="bold")

            # Save if needed
            if save_mode == "directory":
                out_path = os.path.join(save_file, f"ema_{months_name[month]}_{year}.png")
                plt.savefig(out_path, dpi=200, bbox_inches="tight")
            elif save_mode == "prefix":
                out_path = f"{save_file}_{date_name}.png"
                plt.savefig(out_path, dpi=200, bbox_inches="tight")

            if save_file == "":
                plt.show()

    def print_players(self, max_aliases: int = 4):
        alias_list = {}
        for player in self.data.players:
            alias_list[player.name] = []
        for alias, name in self.data.aliases.items():
            alias_list[name].append(alias)
        print("Liste de joueurs :")
        for player in self.data.players:
            print(f"- {player.name} (", end="")
            for ialias in range(min(max_aliases, len(alias_list[player.name]))):
                if ialias != 0:
                    print(", ", end="")
                print(alias_list[player.name][ialias], end="")
            if len(alias_list[player.name]) > max_aliases:
                print(", ...", end="")
            print(")")

    def calc_winning_wind_full_game(self) -> dict[str, list[list[tuple]]]:
        """
        Calculates the frequency of winning a game for each player and each wind
        return frequency tab : {player name: [wind num][place](count, freq by wind)}
        one special player name for the total : 'total'
        one special 5th wind for the total
        """
        freqs = {}
        default_freqs = [[0 for place in range(4)] for wind in range(5)]
        players_with_total = self.data.players + ['total']
        for p in players_with_total:
            freqs[p] = deepcopy(default_freqs)
        for game in self.data.games:
            rank_points = pd.Series(game.end_points).rank()
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                freqs[player_name][wind][4 - int(rank_points[wind])] += 1
                freqs[player_name][4][4 - int(rank_points[wind])] += 1
                freqs['total'][wind][4 - int(rank_points[wind])] += 1
                freqs['total'][4][4 - int(rank_points[wind])] += 1
        for p in players_with_total:
            for wind in range(5):
                S = 0.00000001
                for place in range(4):
                    S += freqs[p][wind][place]
                for place in range(4):
                    freqs[p][wind][place] = (freqs[p][wind][place], freqs[p][wind][place] / S)
        return freqs
    
    def calc_nb_encounters(self) -> dict[str, dict[str, int]]:
        """
        Calculates the number of time each player has played against each other in the tournament
        return count tab : {player 1: {player 2: count}}
        """
        counts = {}
        players_with_total = [p.name for p in self.data.players] + ['total']
        for p1 in players_with_total:
            counts[p1] = {}
            for p2 in players_with_total:
                counts[p1][p2] = 0
        for game in self.data.games:
            counts['total']['total'] += 1
            for a1 in game.players:
                p1 = self.data.aliases[a1]
                counts[p1]['total'] += 1
                counts['total'][p1] += 1
                for a2 in game.players:
                    p2 = self.data.aliases[a2]
                    if p1 != p2:
                        counts[p1][p2] += 1
        return counts
    
    def calc_nemesis(self) -> dict[str, dict[str, dict[str, float]]]:
        stats = {}
        players = [p.name for p in self.data.players]
        alpha = 2
        for p1 in players:
            stats[p1] = {}
            for p2 in players:
                if p1 != p2:
                    stats[p1][p2] = {'nb_wins': 0.0, 'nb_total': 0.0, 'win_rate': 0.0, 'smoothed_rate': 0.0}
        for game in self.data.games:
            for i in range(len(game.players)):
                a1 = self.data.aliases[game.players[i]]
                for j in range(i+1, len(game.players)):
                    a2 = self.data.aliases[game.players[j]]
                    stats[a1][a2]['nb_total'] += 1
                    stats[a2][a1]['nb_total'] += 1
                    if game.end_points[i] < game.end_points[j]:
                        a1, a2 = a2, a1
                    if game.end_points[i] == game.end_points[j]:
                        stats[a1][a2]['nb_wins'] += 0.5
                        stats[a2][a1]['nb_wins'] += 0.5
                    else:
                        stats[a1][a2]['nb_wins'] += 1
                    stats[a1][a2]['win_rate'] = stats[a1][a2]['nb_wins'] / stats[a1][a2]['nb_total']
                    stats[a2][a1]['win_rate'] = stats[a2][a1]['nb_wins'] / stats[a2][a1]['nb_total']
                    stats[a1][a2]['smoothed_rate'] = (stats[a1][a2]['nb_wins'] + alpha) / (stats[a1][a2]['nb_total'] + 2 * alpha)
                    stats[a2][a1]['smoothed_rate'] = (stats[a2][a1]['nb_wins'] + alpha) / (stats[a2][a1]['nb_total'] + 2 * alpha)
        return stats

    def calc_total_winrate(self) -> dict[str, list[int]]:
        """
        Calculates the winrate of each player for each placement
        return winrate tab : {player: [1st place amount, 2nd place amount, ...]}
        """
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = [0.0 for i in range(4)]
        for game in self.data.games:
            sorted_points = sorted(game.end_points, reverse=True)
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                places = []
                for place in range(4):
                    if game.end_points[wind] == sorted_points[place]:
                        places.append(place)
                for place in places:
                    stats[player_name][place] += 1 / len(places)
        return stats

    def calc_monthly_winrate(self) -> dict[str, dict[str, list[int]]]:
        """
        Calculates the winrate of each player for each month
        return winrate tab : {player: month: [1st place amount, 2nd place amount, ...]}
        """
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = {}
        for game in self.data.games:
            sorted_points = sorted(game.end_points, reverse=True)
            month = game.date.month
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                if month not in stats[player_name]:
                    stats[player_name][month] = [0.0 for i in range(4)]
                places = []
                for place in range(4):
                    if game.end_points[wind] == sorted_points[place]:
                        places.append(place)
                for place in places:
                    stats[player_name][month][place] += 1 / len(places)
        return stats

    def calc_placement_list(self) -> dict[str, dict[str, list[int]]]:
        """
        Calculates the placement list of each player for each month
        return placement tab : {player: month: [1st match result, 2nd match result, ...]}
        """
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = {}
        for game in self.data.games:
            sorted_points = sorted(game.end_points, reverse=True)
            month = game.date.month
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                if month not in stats[player_name]:
                    stats[player_name][month] = []
                places = []
                for place in range(4):
                    if game.end_points[wind] == sorted_points[place]:
                        places.append(place+1)
                stats[player_name][month].append(sum(places) / len(places))
        return stats

    def calc_record_hand_stats(self, n = 5) -> dict[str, list]:
        """
        Calculates a handful of records about individual hands.
        Records calculated :
          - best hand (alias 'best_hand'), format : [(player, 1st best hand), (player, 2nd best hand), ...] up to n
          - best self drawn hand (alias 'best_drawn_hand'), format : [(player, 1st best hand), (player, 2nd best hand), ...] up to n
        """
        stats = {
            "best_hand": [],
            "best_drawn_hand": [],
        }
        for game in self.data.games:
            if game.rounds is not None:
                for rnd in game.rounds:
                    if rnd.winner is not None:
                        stats["best_hand"].append((self.data.aliases[rnd.winner], rnd.hand_points))
                        if rnd.discarder is None:
                            stats["best_drawn_hand"].append((self.data.aliases[rnd.winner], rnd.hand_points))
        stats["best_hand"].sort(key = lambda x: x[1], reverse=True)
        stats["best_drawn_hand"].sort(key = lambda x: x[1], reverse=True)
        stats["best_hand"] = stats["best_hand"][:n]
        stats["best_drawn_hand"] = stats["best_drawn_hand"][:n]
        return stats

    def calc_record_game_stats(self, n = 5) -> dict[str, list]:
        """
        Calculates a handful of records about individual games.
        Records calculated :
          - best upset (alias 'best_upset'), format : [(winning player, losing player, elo difference), ...] up to n
          - best final score (alias 'best_score'), format : [(player, 1st best score), (player, 2nd best score), ...] up to n
          - worst final score (alias 'worst_score'), format : [(player, 1st worst score), (player, 2nd worst score), ...] up to n
        """
        stats = {
            "best_upset": [],
            "best_score": [],
        }
        for igame, game in enumerate(self.data.games):
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                stats["best_score"].append((player_name, game.end_points[wind]))
                for other_wind in range(wind):
                    other_name = self.data.aliases[game.players[other_wind]]
                    if igame == 0:
                        other_elo = self.data.players[self.data.get_player_id(other_name)].base_elo
                        player_elo = self.data.players[self.data.get_player_id(player_name)].base_elo
                    else:
                        other_elo = self.data.elo[igame-1][other_name]
                        player_elo = self.data.elo[igame-1][player_name]
                    elo_diff = other_elo - player_elo
                    player_won = game.end_points[wind] > game.end_points[other_wind]
                    if player_won:
                        stats["best_upset"].append((player_name, other_name, elo_diff))
                    else:
                        stats["best_upset"].append((other_name, player_name, -elo_diff))
        stats["best_upset"].sort(key = lambda x: x[2], reverse=True)
        stats["best_score"].sort(key = lambda x: x[1], reverse=True)
        stats["worst_score"] = stats["best_score"][-n:][::-1]
        stats["best_score"] = stats["best_score"][:n]
        stats["best_upset"] = stats["best_upset"][:n]
        return stats

    def calc_hand_stats(self) -> dict[str, dict[str, Any]]:
        """
        Calculates a handful of statistics about hands of players.
        Stats calculated :
          - winning hands (alias 'won'), format : dict
            - proportion of won hands (alias 'win_prob')
            - proportion of self-drawn hands among won hands (alias 'self_prob')
            - average value of hand (alias 'avg_value')
            - list of values (alias 'value_list')
          - proportion of walls (alias 'wall'), format : float
          - dealt-in hands (alias 'deal_in'), format : dict
            - proportion of deal-in (alias 'deal_in_prob')
            - average value of deal-in (alias 'avg_value')
            - list of values (alias 'value_list')
        - total hands played (alias 'total')
        """
        # Stats initialization
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = {
                'won': {'value_list': [], 'self_prob': 0},
                'wall': 0,
                'deal_in': {'value_list': []},
                'total': 0
            }

        # Stats querying
        for game in self.data.games:
            if game.rounds is not None:
                for rnd in game.rounds:
                    for alias in game.players:
                        player_name = self.data.aliases[alias]
                        if rnd.winner is None:
                            stats[player_name]['wall'] += 1
                        elif rnd.winner == alias:
                            stats[player_name]['won']['value_list'].append(rnd.hand_points)
                            if rnd.discarder is None:
                                stats[player_name]['won']['self_prob'] += 1
                        elif rnd.discarder == alias:
                            stats[player_name]['deal_in']['value_list'].append(rnd.hand_points)
                        stats[player_name]['total'] += 1

        # Stats grouping
        for p in players:
            total_rounds = stats[p]['total']
            if total_rounds == 0:
                del stats[p]
            else:
                stats[p]['won']['win_prob'] = len(stats[p]['won']['value_list']) / total_rounds
                if len(stats[p]['won']['value_list']) > 0:
                    stats[p]['won']['self_prob'] /= len(stats[p]['won']['value_list'])
                    stats[p]['won']['avg_value'] = mean(stats[p]['won']['value_list'])
                else:
                    stats[p]['won']['self_prob'] = 0.0
                    stats[p]['won']['avg_value'] = 0.0
                stats[p]['wall'] /= total_rounds
                stats[p]['deal_in']['deal_in_prob'] = len(stats[p]['deal_in']['value_list']) / total_rounds
                if len(stats[p]['deal_in']['value_list']) > 0:
                    stats[p]['deal_in']['avg_value'] = mean(stats[p]['deal_in']['value_list'])
                else:
                    stats[p]['deal_in']['avg_value'] = 0.0
        return stats