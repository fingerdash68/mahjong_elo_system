import matplotlib
# print(matplotlib.get_backend())
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from data import *
import os
from pprint import pprint
from statistics import mean
from typing import Any
from math import sqrt
import numpy as np

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

    def plot_winrate(self, folder: str):
        """
        Creates a winrate graph for each player and saves it as:
            folder/player_name/winrate.png

        The graph contains:
            - Total placement distribution
            - Monthly placement distributions
            - Placement of every individual game
        """
        total_winrate = self.calc_total_winrate()
        monthly_winrate = self.calc_monthly_winrate()
        placement_list = self.calc_placement_list()
        players = [p.name for p in self.data.players]
        # Find all months that appear in the tournament
        months = sorted({
            month
            for player in monthly_winrate.values()
            for month in player
        }, key = lambda x: (x - 9) % 12)

        for player in players[:]:
            print(f"winrate graph for player {player}")

            # Create player directory
            player_folder = os.path.join(folder, player)
            os.makedirs(player_folder, exist_ok=True)

            placement_colors = ["#2EAD69","#66C2A5","#F6C453","#E45756"]
            placement_labels = ["1er", "2e", "3e", "4e"]
            months_labels = ["", "Jan", "Fev", "Mars", "Avr", "Mai", "Juin", "Juil", "Aout", "Sep", "Oct", "Nov", "Dec"]

            fig = plt.figure(figsize=(12, 8))
            gs = fig.add_gridspec(6, 5)

            # ==================================================
            # Total winrate
            # ==================================================

            total_ax = fig.add_subplot(gs[:2, :])

            filtered = [(value, label, color) for value, label, color in zip(total_winrate[player], placement_labels, placement_colors) if value > 0]
            values, labels, colors = zip(*filtered)
            total_ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                colors=colors
            )
            total_ax.set_title(f"{player} - Taux de victoire")

            # ==================================================
            # Monthly winrate
            # ==================================================

            for i, month in enumerate(months):
                ax_row = i // ((len(months) + 1)//2) + 2
                ax_col = i % ((len(months) + 1)//2)
                month_ax = fig.add_subplot(gs[ax_row, ax_col])
                if month not in monthly_winrate[player]:
                    month_ax.pie([1], colors=["white"])
                    month_ax.text(0, 0, "Aucune partie", ha="center", va="center")
                else:
                    filtered = [(value, label, color) for value, label, color in zip(monthly_winrate[player][month], placement_labels, placement_colors) if value > 0]
                    values, labels, colors = zip(*filtered)
                    if len(values) == 1:
                        month_ax.pie(values, labels=labels, colors=colors, textprops={"fontsize": 8})
                        month_ax.text(0, 0, "100%", ha="center", va="center", fontsize=8)
                    else:
                        month_ax.pie(
                            values,
                            labels=labels,
                            autopct="%1.0f%%",
                            colors=colors,
                            textprops={"fontsize": 8}
                        )
                month_ax.set_title(months_labels[month])

            # ==================================================
            # Individual games
            # ==================================================

            full_placement = []
            for places in placement_list[player].values():
                full_placement.extend(places)
            indiv_ax = fig.add_subplot(gs[4:, :])
            indiv_ax.plot(range(1, len(full_placement)+1), full_placement)
            for i, place in enumerate(full_placement):
                indiv_ax.plot(i+1, place, marker="o", markersize=2, color=placement_colors[int(place)])

            indiv_ax.set_yticks(
                range(4),
                labels=placement_labels,
            )
            indiv_ax.invert_yaxis()
            for place in range(4):
                indiv_ax.axhline(place, color="#999999", linewidth=0.5, linestyle="--")

            nb_games = 0
            x_ticks = []
            x_ticks_labels = []
            for month, places in placement_list[player].items():
                nb_games += len(places)
                indiv_ax.axvline(nb_games + 0.5, color="#999999", linewidth=0.75, linestyle="-")
                x_ticks.append(nb_games - len(places)/2 + 0.5)
                x_ticks_labels.append(months_labels[month])
            indiv_ax.set_xticks(x_ticks)
            indiv_ax.set_xticklabels(x_ticks_labels, rotation=45)

            fig.savefig(os.path.join(player_folder, "winrate.png"))
            plt.close(fig)

    def plot_hand_stats(self, folder: str):
        """
        Creates a winrate graph for each player and saves it as:
            folder/player_name/hand_stats.png
        
        The graph contains:
            - Hand result distribution
            - Winning hands statistics
            - Deal-in hands statistics
        """
        hand_stats = self.calc_hand_stats()
        evolution_stats = self.calc_mid_game_evolution()
        players = [p.name for p in self.data.players]
        
        for player in players[:]:
            print(f"hand stats graph for player {player}")

            # Create player directory
            player_folder = os.path.join(folder, player)
            os.makedirs(player_folder, exist_ok=True)

            result_colors = ["#2EAD69", "#E45756", "#E9B949", "#B0B0B0"]
            winning_colors = ["#E45756", "#4C9BD1"]

            fig = plt.figure(figsize=(8, 8))
            gs = fig.add_gridspec(10, 7)

            # ==================================================
            # Hand overview
            # ==================================================

            overview_ax = fig.add_subplot(gs[:1, :])
            win = hand_stats[player]['won']['win_prob']
            deal_in = hand_stats[player]['deal_in']['deal_in_prob']
            wall = hand_stats[player]['wall']
            bar_fractions = [0, win, win + deal_in, win + deal_in + wall, 1]
            bar_centers = [win/2, win + deal_in/2, win + deal_in + wall/2, (1 + win + deal_in + wall)/2]
            overview_labels = ["Mahjong", "Donné", "Mur", "Autre"]
            for i in range(1, len(bar_fractions)):
                percent = bar_fractions[i] - bar_fractions[i-1]
                overview_ax.barh(0, percent, left=bar_fractions[i-1], color=result_colors[i-1])
                overview_ax.text(bar_fractions[i-1] + percent/2, 0, f"{percent*100:.1f}%", ha="center", va="center")
                overview_ax.axvline(bar_fractions[i], color="#000000", linewidth=0.5, linestyle="-")
            overview_ax.set_xlim(0, 1)
            overview_ax.set_yticks([])
            overview_ax.set_xticks(bar_centers)
            overview_ax.set_xticklabels(overview_labels)
            overview_ax.set_title("Répartition des mains", fontsize=14, pad=10)

            # ==================================================
            # Winning hands
            # ==================================================

            winning_draw_ax = fig.add_subplot(gs[3:4, :3])
            self_prob = hand_stats[player]['won']['self_prob']
            bar_fractions = [0, self_prob, 1]
            bar_centers = [self_prob/2, (1 + self_prob)/2]
            self_labels = ["Tiré", "Donné"]
            for i in range(1, len(bar_fractions)):
                percent = bar_fractions[i] - bar_fractions[i-1]
                winning_draw_ax.barh(0, percent, left=bar_fractions[i-1], color=winning_colors[i-1])
                winning_draw_ax.text(bar_fractions[i-1] + percent/2, 0, f"{percent*100:.1f}%", ha="center", va="center")
                winning_draw_ax.axvline(bar_fractions[i], color="#000000", linewidth=0.5, linestyle="-")
            winning_draw_ax.set_xlim(0, 1)
            winning_draw_ax.set_yticks([])
            winning_draw_ax.set_xticks(bar_centers)
            winning_draw_ax.set_xticklabels(self_labels)
            winning_draw_ax.set_title("Proportion de tirés", fontsize=14, pad=10)

            distrib_ax = fig.add_subplot(gs[5:7, :3])
            self_values = hand_stats[player]['won']['self_list']
            direct_values = hand_stats[player]['won']['deal_in_list']
            if self_values or direct_values:
                start_x = min(self_values + direct_values)
                end_x = max(self_values + direct_values)
                bins = list(range(start_x, end_x+2))
            else:
                start_x, end_x, bins = 8, 88, [8, 88]
            distrib_ax.hist(
                [self_values, direct_values],
                bins=bins,
                stacked=True,
                rwidth=0.8,
                color=winning_colors
            )
            alpha = 0.1
            distrib_ax.set_xscale("function", functions=(lambda x: x**alpha, lambda x: x**(1/alpha)))
            default_ticks = [8, 12, 16, 20, 24, 32, 48, 64, 88, 120, 150]
            x_ticks = [tick for tick in default_ticks if tick >= start_x and tick <= end_x]
            if x_ticks: x_ticks.pop()
            x_ticks.append(end_x)
            distrib_ax.set_xticks(x_ticks)
            distrib_ax.set_title("Répartition des mahjongs", fontsize=14, pad=10)

            stats_ax = fig.add_subplot(gs[7:8, :3])
            stats_ax.axis("off")
            highest_win = np.max(self_values + direct_values) if len(self_values + direct_values) > 0 else 0
            mean_win = np.mean(self_values + direct_values) if len(self_values + direct_values) > 0 else 0
            std_win = np.std(self_values + direct_values) if len(self_values + direct_values) > 0 else 0
            stats_ax.text(
                0.5, 0.0,
                f"Max: {highest_win} pts\n"
                f"Moy: {mean_win:.1f} pts\n"
                f"Ecart-type: {std_win:.1f} pts",
                ha="center",
                va="center"
            )

            # ==================================================
            # Deal-in hands
            # ==================================================

            distrib_ax = fig.add_subplot(gs[3:5, 4:])
            deal_in_values = hand_stats[player]['deal_in']['value_list']
            if deal_in_values:
                start_x = min(deal_in_values)
                end_x = max(deal_in_values)
                bins = list(range(start_x, end_x+2))
            else:
                start_x, end_x, bins = 8, 88, [8, 88]
            distrib_ax.hist(
                deal_in_values,
                bins=bins,
                rwidth=0.8,
                color=winning_colors[1]
            )
            alpha = 0.1
            distrib_ax.set_xscale("function", functions=(lambda x: x**alpha, lambda x: x**(1/alpha)))
            default_ticks = [8, 12, 16, 20, 24, 32, 48, 64, 88, 120, 150]
            x_ticks = [tick for tick in default_ticks if tick >= start_x and tick <= end_x]
            if x_ticks: x_ticks.pop()
            x_ticks.append(end_x)
            distrib_ax.set_xticks(x_ticks)
            distrib_ax.set_title("Répartition des donnés", fontsize=14, pad=10)

            stats_ax = fig.add_subplot(gs[5:6, 4:])
            stats_ax.axis("off")
            highest_deal_in = np.max(deal_in_values) if len(deal_in_values) > 0 else 0
            mean_deal_in = np.mean(deal_in_values) if len(deal_in_values) > 0 else 0
            std_deal_in = np.std(deal_in_values) if len(deal_in_values) > 0 else 0
            stats_ax.text(
                0.5, 0.0,
                f"Max: {highest_deal_in} pts\n"
                f"Moy: {mean_deal_in:.1f} pts\n"
                f"Ecart-type: {std_deal_in:.1f} pts",
                ha="center",
                va="center"
            )

            # ==================================================
            # Mid-game evolution
            # ==================================================

            fig.savefig(os.path.join(player_folder, "hand_stats.png"))
            plt.close(fig)



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
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                places = self._calc_placement_list_from_scores(game.end_points[wind], game.end_points)
                for place in places:
                    stats[player_name][place] += 1 / len(places)
        return stats

    def calc_monthly_winrate(self) -> dict[str, dict[int, list[int]]]:
        """
        Calculates the winrate of each player for each month
        return winrate tab : {player: month: [1st place amount, 2nd place amount, ...]}
        """
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = {}
        for game in self.data.games:
            month = game.date.month
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                if month not in stats[player_name]:
                    stats[player_name][month] = [0.0 for i in range(4)]
                places = self._calc_placement_list_from_scores(game.end_points[wind], game.end_points)
                for place in places:
                    stats[player_name][month][place] += 1 / len(places)
        return stats

    def calc_placement_list(self) -> dict[str, dict[int, list[int]]]:
        """
        Calculates the placement list of each player for each month
        return placement tab : {player: month: [1st match result, 2nd match result, ...]}
        """
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = {}
        for game in self.data.games:
            month = game.date.month
            for wind in range(4):
                player_name = self.data.aliases[game.players[wind]]
                if month not in stats[player_name]:
                    stats[player_name][month] = []
                places = self._calc_placement_list_from_scores(game.end_points[wind], game.end_points)
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
            - list of dealt-in values (alias 'deal_in_list')
            - list of self-drawn values (alias 'self_list')
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
                'won': {'value_list': [], 'self_prob': 0, 'deal_in_list': [], 'self_list': []},
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
                                stats[player_name]['won']['self_list'].append(rnd.hand_points)
                            else:
                                stats[player_name]['won']['deal_in_list'].append(rnd.hand_points)
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

    def calc_opponent_winrate(self) -> dict[str, dict[str, dict[str, float]]]:
        """
        Calculates the number of times each player got placed better than each other player.
        A draw counts as half a better place. The total games played is found in the self player's field.
        return frequency dict : {player: {other1: {'won':..., 'total':...}}}
        """
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = {}
            for p2 in players:
                stats[p][p2] = {'won': 0.0, 'total': 0.0}
        for game in self.data.games:
            for wind in range(4):
                for other_wind in range(4):
                    player_name = self.data.aliases[game.players[wind]]
                    other_name = self.data.aliases[game.players[other_wind]]
                    if game.end_points[wind] > game.end_points[other_wind]:
                        stats[player_name][other_name]['won'] += 1.0
                    elif game.end_points[wind] == game.end_points[other_wind]:
                        stats[player_name][other_name]['won'] += 0.5
                    stats[player_name][other_name]['total'] += 1.0
        return stats

    def calc_mid_game_evolution(self) -> dict[str, list[list[float]]]:
        """
        Calculates the evolution of the players placements from midgame to endgame.
        return evolution tab : {player: [1st midgame: [1st endgame, 2nd endgame, ...], 2nd midgame: [...], ...]}
        """
        stats = {}
        players = [p.name for p in self.data.players]
        for p in players:
            stats[p] = [[0.0 for i in range(4)] for j in range(4)]
        for game in self.data.games:
            if game.rounds is not None:
                scores = {}
                for player_name in game.players:
                    scores[self.data.aliases[player_name]] = 0
                for rnd in game.rounds[:len(game.rounds)//2]:
                    winner = rnd.winner
                    discarder = rnd.discarder
                    if winner is not None:
                        winner = self.data.aliases[winner]
                    if discarder is not None:
                        discarder = self.data.aliases[discarder]
                    if winner is not None:
                        for alias in game.players:
                            player_name = self.data.aliases[alias]
                            if player_name != winner:
                                scores[player_name] -= 8
                                scores[winner] += 8
                            if player_name == discarder or discarder is None:
                                scores[player_name] -= rnd.hand_points
                                scores[winner] += rnd.hand_points
                    if rnd.penalties is not None:
                        for alias, pen in rnd.penalties.items():
                            name = self.data.aliases[alias]
                            scores[name] += pen
                score_list = [scores[self.data.aliases[p]] for p in game.players]
                for wind in range(4):
                    player_name = self.data.aliases[game.players[wind]]
                    mid_places = self._calc_placement_list_from_scores(score_list[wind], score_list)
                    end_places = self._calc_placement_list_from_scores(game.end_points[wind], game.end_points)
                    nb_places = len(mid_places) * len(end_places)
                    for mid in mid_places:
                        for end in end_places:
                            stats[player_name][mid][end] += 1 / nb_places
        return stats

    def _calc_placement_list_from_scores(self, score: int, scores: list[int]):
        """
        Returns the list of places that got the same score as the player
        """
        places = []
        sorted_scores = sorted(scores, reverse=True)
        for i in range(len(scores)):
            if sorted_scores[i] == score:
                places.append(i)
        return places