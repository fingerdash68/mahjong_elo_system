import json
import pandas as pd # type: ignore
from data import *
import datetime as dt

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
        
        # Ajout partie
        return self._try_to_add_game(data, names, end_points, date, rounds)
    
    def load_games_excel(self, data: Data, file_path: str) -> tuple[int, str]:
        xlsx = pd.ExcelFile(file_path)
        df_games = pd.read_excel(xlsx, sheet_name="Donnees", header=None)
        df_players = pd.read_excel(xlsx, sheet_name="EMA points", header=None)

        # Chargement des joueurs
        for row_num in range(2, len(df_players)):
            name = str(df_players.iloc[row_num, 0])
            base_elo = float(df_players.iloc[row_num, 1]) # type: ignore
            data.add_player(Player(name, base_elo))

        # Chargement des parties
        for row_num in range(0, len(df_games), 4):
            date_cell = df_games.iloc[row_num+1, 5]
            if pd.isna(date_cell):
                continue
            date = dt.datetime.fromisoformat(str(date_cell))
            player_names = []
            player_scores = []
            for wind in range(4):
                name = str(df_games.iloc[row_num+1, 1 + wind])
                score = int(df_games.iloc[row_num+2, 1 + wind]) # type: ignore
                player_names.append(name)
                player_scores.append(score)
            err_code, err_mess = data.add_game(Game(player_names, player_scores, date))
            if err_code != 0:
                return (err_code, err_mess)


        return (0, "")


    def load_game_std_input(self, data: Data) -> tuple[int, str]:
        verif = False
        while not(verif): 
            names, end_points, date = self._read_game_input()
            print("DEUXIEME VERIFICATION")
            names_v, end_points_v, date_v = self._read_game_input()
            if (names, end_points, date) == (names_v, end_points_v, date_v):
                verif = True
            else:
                print("Verification invalide, parties differentes")
        return self._try_to_add_game(data, names, end_points, date, rounds=[])
        
    
    def _try_to_add_game(self, data: Data, names: list[str], end_points: list[int], date: dt.datetime, rounds: list[Round]) -> tuple[int, str]:
        for name in names:
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
        err_code, err_mess = data.add_game(Game(names, end_points, date, rounds))
        return (err_code, err_mess)

    
    def _read_game_input(self) -> tuple[list[str], list[int], dt.datetime]:
        winds = ['Est', 'Sud', 'West', 'Nord']
        names = []
        end_points = []
        for wind in winds:
            print(f"Nom du joueur {wind} : ", end="")
            names.append(input())
            print(f"Points du joueur {wind} : ", end="")
            end_points.append(int(input()))
        print("Date de la partie (DD/MM/YYYY hh:mm:ss) : ", end="")
        date = dt.datetime.strptime(input(), "%d/%m/%Y %H:%M:%S")
        return (names, end_points, date)