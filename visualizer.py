import matplotlib.pyplot as plt
from data import *
import os

class Visualizer:
    def __init__(self, data: Data):
        self.data = data
    
    def plot_elos(self, players_per_plot: int = 3, save_file: str = ""):
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
                plt.plot(dates, elo_values, label=player)

            plt.xlabel("Date")
            plt.ylabel("Elo Rating")
            plt.title(f"Elo Progression — {', '.join(group)}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            # Save if needed
            if save_mode == "directory":
                out_path = os.path.join(save_file, f"elo_{fig_index}.png")
                plt.savefig(out_path)
            elif save_mode == "prefix":
                out_path = f"{save_file}_{fig_index}.png"
                plt.savefig(out_path)
            
            # Show only when not saving
            if save_file == "":
                plt.show()

            plt.close()
            fig_index += 1

    def plot_emas(self, save_file: str = ""):
        pass