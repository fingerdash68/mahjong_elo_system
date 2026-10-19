from data import *
from loaders import *
from visualizer import *
from utils import *
from pathlib import Path
import json
from pprint import pprint
import matplotlib.pyplot as plt
import datetime as dt

DATA_SAVE_FILE = "./games.json"
IMPORT_FOLDER = "./import_files/"

data = Data()
if Path(DATA_SAVE_FILE).exists():
    with open(DATA_SAVE_FILE, "r") as f:
        data_dict = json.load(f)
        data = Data.from_dict(data_dict)
loader = DataLoader(data)
visualizer = Visualizer(data)

# pprint(visualizer.calc_total_winrate())
# pprint(visualizer.calc_monthly_winrate())
# pprint(visualizer.calc_placement_list())
# pprint(visualizer.calc_record_hand_stats())
# pprint(visualizer.calc_record_game_stats())
# pprint(visualizer.calc_hand_stats())
# pprint(visualizer.calc_opponent_winrate())
# pprint(visualizer.calc_mid_game_evolution())
# visualizer.plot_winrate("stats_2025-26")
# visualizer.plot_hand_stats("stats_2025-26")
# visualizer.plot_opponent_winrate("stats_2025-26")

continuer = True
while continuer:
    print("""
        (1) Charger un fichier excel
        (2) Charger un fichier csv
        (3) Charger tous les fichiers dans import files
        (4) Sauvegarder dans un fichier json
        (5) Afficher les elos
        (6) Afficher les emas
        (7) Stats speciales
        (8) Ajouter une partie manuellement
        (9) Supprimer une partie
        (10) Supprimer un joueur
        (11) Afficher la liste des joueurs
        (99) Terminal de commandes (dev only)
        (0) Quitter
    """)
    choix = int(input())
    if choix == 1:
        file_path = input("Entrez le nom du fichier excel : ")
        err_code, err_mess = loader.load_games_excel(file_path)
        if err_code != 0:
            print("Erreur :", err_mess)
    elif choix == 2:
        file_path = input("Entrez le nom du fichier csv : ")
        err_code, err_mess = loader.load_game_csv(file_path)
        if err_code != 0:
            print("Erreur :", err_mess)
    elif choix == 3:
        processed_files = []
        for file in Path(IMPORT_FOLDER).iterdir():
            if file.is_file():
                if file.suffix == ".xlsx":
                    print("Chargement fichier", file.name)
                    err_code, err_mess = loader.load_games_excel(IMPORT_FOLDER + file.name)
                    if err_code != 0:
                        print("Erreur :", err_mess)
                    else:
                        processed_files.append(IMPORT_FOLDER + file.name)
                if file.suffix == ".csv":
                    print("Chargement fichier", file.name)
                    err_code, err_mess = loader.load_game_csv(IMPORT_FOLDER + file.name)
                    if err_code != 0:
                        print("Erreur :", err_mess)
                    if err_code == 0 or err_code == 1:
                        processed_files.append(IMPORT_FOLDER + file.name)
            if len(processed_files) % 10 == 0 and len(processed_files) > 0:
                print("Sauvegarder l'avancement ? (y/n) ", end="")
                choix = input().lower()
                if choix == "y":
                    with open(DATA_SAVE_FILE, "w") as f:
                        json.dump(data.to_dict(), f, indent=4)
                    for file_name in processed_files:
                        os.remove(file_name)
                    processed_files = []
        for file_name in processed_files:
            os.remove(file_name)
    elif choix == 4:
        file_path = input("Entrez le nom du fichier json (vide pour defaut) : ")
        if file_path == "":
            file_path = DATA_SAVE_FILE
        with open(file_path, "w") as f:
            json.dump(data.to_dict(), f, indent=4)
    elif choix == 5:
        players_per_plot = input("Entrez le nombre de joueur par graphe : ")
        if players_per_plot == "":
            players_per_plot = "6"
        players_per_plot = int(players_per_plot)
        save_path = input("Entrez le chemin d'enregistrement : ")
        visualizer.plot_elos(players_per_plot, save_path)
    elif choix == 6:
        save_path = input("Entrez le chemin d'enregistrement : ")
        visualizer.plot_emas(save_path)
    elif choix == 7:
        print("""
            (1) Stats par vent
            (2) Enregistrer elos
            (3) Enregistrer ema
            (4) Nombre de rencontres par joueur
            (5) Stats nemesis
            (6) Extraire par date ou joueur
        """)
        choix2 = int(input())
        if choix2 == 1:
            freqs = visualizer.calc_winning_wind_full_game()
            for p in data.players:
                print(p.name, ":")
                print_freqs(freqs[p.name])
            print("TOTAL :")
            print_freqs(freqs['total'])
        elif choix2 == 2:
            file_path = input("Entrez le nom du fichier ou enregistrer les elos : ")
            with open(file_path, "w") as f:
                json.dump(data._get_readable_elo_dict(), f, indent=4)
        elif choix2 == 3:
            file_path = input("Entrez le nom du fichier ou enregistrer les emas : ")
            with open(file_path, "w") as f:
                json.dump(data.ema, f, indent=4)
        elif choix2 == 4:
            counts = visualizer.calc_nb_encounters()
            for p, count in counts.items():
                print(f"Rencontres de {p} :")
                print_counts(count)
        elif choix2 == 5:
            stats = visualizer.calc_nemesis()
            for p, stat in stats.items():
                print(f"Taux de victoire de {p} :")
                print()
                print_nemesis(stat)
                print()
        elif choix2 == 6:
            start_day = input("Entrez la date de depart (jj/mm/yy) : ")
            end_day = input("Entrez la date de fin (jj/mm/yy) : ")
            player_name = input("Entrez le nom du joueur : ")
            with_detail = input("Avec le detail ? (y/n) ") == "y"
            if start_day == "":
                start_day = None
            else:
                start_day = dt.datetime.strptime(start_day, '%d/%m/%y').date()
            if end_day == "":
                end_day = None
            else:
                end_day = dt.datetime.strptime(end_day, '%d/%m/%y').date()
            if player_name == "":
                player_name = None
            games_detail = visualizer.extract_games_from_day_and_player(start_day, end_day, player_name, with_detail)
            print(f"{len(games_detail)} parties trouvees.")
            for game_detail in games_detail:
                print_game(data, game_detail[0], game_detail[1])
    elif choix == 8:
        date = input("Date et horaire de la partie (jj/mm/yy HH:MM:SS) : ")
        date = dt.datetime.strptime(date, "%d/%m/%y %H:%M:%S")
        players = []
        end_points = []
        for wind in ["Est", "Sud", "Ouest", "Nord"]:
            players.append(input(f"Nom du joueur {wind} : "))
            end_points.append(int(input(f"Points du joueur {wind} : ")))
        loader._try_to_add_game(players, end_points, date, [])
    elif choix == 9:
        for igame, game in enumerate(data.games):
            print(f"{igame}) ", end="")
            print_game(data, game)
        rem_game_nb = int(input("Entrez le numero de la partie a supprimer : "))
        if rem_game_nb < 0 or rem_game_nb >= len(data.games):
            print("Numero invalide")
        else:
            game = data.games[rem_game_nb]
            print("Partie supprimee : ", end="")
            print_game(data, game)
            data.remove_games([rem_game_nb])
    elif choix == 10:
        player_name = input("Entrez le nom du joueur a supprimer : ")
        err_code, err_mess = loader.remove_player(player_name)
        if err_code != 0:
            print("Erreur :", err_mess)
    elif choix == 11:
        visualizer.print_players()
    elif choix == 99:
        commands = []
        while True:
            comm = input("> ")
            if comm == "quit":
                break
            commands.append(comm)
            exec(comm)
    elif choix == 0:
        continuer = False

with open(DATA_SAVE_FILE, "w") as f:
    json.dump(data.to_dict(), f, indent=4)