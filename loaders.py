import json
import pandas as pd # type: ignore
from data import *

class DataLoader:
    def load_game_csv(self, data: Data, file_path: str) -> tuple[int, str]:
        # Pretraitement
        df = pd.read_csv(file_path)
        df['Game start date'] = pd.to_datetime(df['Game start date'], format="%a %b %d %H:%M:%S GMT%z %Y", errors="coerce").dt.tz_convert(None)
        df.columns = df.columns.str.removeprefix("Points ")

        # Extraction donnees base
        date = df['Game start date'].iloc[0]
        names = df.columns[4:8].tolist()
        end_points = []
        for name in names:
            end_points.append(int(df[name].iloc[-1]))
            while not(name in data.aliases):
                print(f"Joueur '{name}' inconnu.")
                print("(1) Ajouter en tant que nouveau joueur")
                print("(2) Ajouter en tant qu'alias pour un joueur existant")
                choix = int(input())
                if not(choix in [1, 2]):
                    continue
                if choix == 1:
                    print("Elo pour le joueur : ", end="")
                    elo = float(input())
                    print("Nom officiel du joueur : ", end="")
                    player_name = input()
                    err_code, err_mess = data.add_player(Player(player_name, elo))
                    if err_code == 0:
                        err_code, err_mess = data.add_alias(name, player_name)
                if choix == 2:
                    print("Joueur dont c'est l'alias : ", end="")
                    player_name = input()
                    err_code, err_mess = data.add_alias(name, player_name)
                if err_code != 0:
                    print("Erreur :", err_mess)
        
        # Extraction rounds
        rounds = []
        for row_num in range(0, len(df), 2):
            winner = df['Winner'].iloc[row_num]
            if winner == "-":
                winner = None
            discarder = df['Discarder'].iloc[row_num]
            if discarder == "-":
                discarder = None
            hand_points = df['Hand Points'].iloc[row_num]
            penalties = {}
            for name in names:
                penalties[name] = df['Penalty ' + name].iloc[row_num]
            rounds.append(Round(winner=winner, discarder=discarder, hand_points=hand_points, penalties=penalties))
        rounds = []
        
        # Ajout partie
        err_code, err_mess = data.add_game(Game(names, end_points, date, rounds))
        if err_code != 0:
            return (err_code, err_mess)
        return (0, "")