from data import *
from loaders import *
from pathlib import Path
import json
from pprint import pprint

DATA_SAVE_FILE = "./games.json"
IMPORT_FOLDER = "./import_files/"

loader = DataLoader()
data = Data()
if Path(DATA_SAVE_FILE).exists():
    with open(DATA_SAVE_FILE, "r") as f:
        data_dict = json.load(f)
        data = Data.from_dict(data_dict)
# loader.load_games_excel(data, "./import_files/mahjong_elo.xlsx")
data.add_player(Player('Kevin', 1200))
data.add_player(Player('Christophe', 1000))
data.add_player(Player('Delphine', 1000))
data.add_player(Player('Ghislaine', 900))
data.add_player(Player('Guilhem', 1100))
data.add_alias('Kev', 'Kevin')
data.add_alias('Kevin 52', 'Kevin')
data.add_alias('Christophe 25', 'Christophe')
data.add_alias('Delphine 99', 'Delphine')
data.add_alias('Ghislaine 51', 'Ghislaine')
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
        (0) Quitter
    """)
    choix = int(input())
    if choix == 1:
        file_path = input("Entrez le nom du fichier excel : ")
        err_code, err_mess = loader.load_games_excel(data, file_path)
        if err_code != 0:
            print("Erreur :", err_mess)
    elif choix == 2:
        file_path = input("Entrez le nom du fichier csv : ")
        err_code, err_mess = loader.load_game_csv(data, file_path)
        if err_code != 0:
            print("Erreur :", err_mess)
    elif choix == 3:
        for file in Path(IMPORT_FOLDER).iterdir():
            if file.is_file():
                if file.suffix == ".xlsx":
                    print("Chargement fichier", file.name)
                    err_code, err_mess = loader.load_games_excel(data, IMPORT_FOLDER + file.name)
                    if err_code != 0:
                        print("Erreur :", err_mess)
                if file.suffix == ".csv":
                    print("Chargement fichier", file.name)
                    err_code, err_mess = loader.load_game_csv(data, IMPORT_FOLDER + file.name)
                    if err_code != 0:
                        print("Erreur :", err_mess)
    elif choix == 4:
        with open(DATA_SAVE_FILE, "w") as f:
            json.dump(data.to_dict(), f, indent=4)
    elif choix == 0:
        continuer = False

with open(DATA_SAVE_FILE, "w") as f:
    json.dump(data.to_dict(), f, indent=4)