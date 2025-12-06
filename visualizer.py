import matplotlib.pyplot as plt
from data import *
import os

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
                for i in range(len(dates)):
                    if i == len(dates) - 1 or (dates[i+1] - dates[i]).days >= 1:
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
                if stats['rank'] != -1:
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