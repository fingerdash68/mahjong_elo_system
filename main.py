from data import *
from loaders import *
from visualizer import *
from pathlib import Path
import json
from pprint import pprint
import matplotlib.pyplot as plt

DATA_SAVE_FILE = "./games.json"
IMPORT_FOLDER = "./import_files/"

data = Data()
if Path(DATA_SAVE_FILE).exists():
    with open(DATA_SAVE_FILE, "r") as f:
        data_dict = json.load(f)
        data = Data.from_dict(data_dict)
loader = DataLoader(data)
visualizer = Visualizer(data)
# loader.load_games_excel(data, "./import_files/mahjong_elo.xlsx")
# data.add_player(Player('Kevin', 1200))
# data.add_player(Player('Christophe', 1000))
# data.add_player(Player('Delphine', 1000))
# data.add_player(Player('Ghislaine', 900))
# data.add_player(Player('Guilhem', 1100))
# data.add_alias('Kev', 'Kevin')
# data.add_alias('Kevin 52', 'Kevin')
# data.add_alias('Christophe 25', 'Christophe')
# data.add_alias('Delphine 99', 'Delphine')
# data.add_alias('Ghislaine 51', 'Ghislaine')
# file_path = "import_files/04_10_2025 16_45.csv"
# print(loader.load_game_csv(data, file_path))
# print(loader.load_game_csv(data, file_path))
# print(loader.load_game_std_input(data))

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
        (8) Supprimer un joueur
        (9) Afficher la liste des joueurs
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
        """)
        choix2 = int(input())
        if choix2 == 1:
            freqs = visualizer.calc_winning_wind_full_game()
            def print_freqs(freq):
                winds = ['East', 'South', 'West', 'North', 'Total']
                places = ['1st', '2nd', '3rd', '4th']
                for wind in range(len(winds)):
                    print(f"\t{winds[wind]} : ", end="")
                    for place in range(len(places)):
                        if place != 0: print(", ", end="")
                        print(f"{places[place]} : {freq[wind][place][0]} ({round(100*freq[wind][place][1], 1)}%)", end="")
                    print()
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
    elif choix == 8:
        player_name = input("Entrez le nom du joueur a supprimer : ")
        err_code, err_mess = loader.remove_player(player_name)
        if err_code != 0:
            print("Erreur :", err_mess)
    elif choix == 9:
        visualizer.print_players()
    elif choix == 0:
        continuer = False

with open(DATA_SAVE_FILE, "w") as f:
    json.dump(data.to_dict(), f, indent=4)