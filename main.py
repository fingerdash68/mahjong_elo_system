from data import *
from loaders import *
import json
from pprint import pprint

loader = DataLoader()
data = Data()
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
file_path = "import_files/04_10_2025 16_45.csv"
print(loader.load_game_csv(data, file_path))
print(loader.load_game_csv(data, file_path))
print(loader.load_game_std_input(data))
print("DATA :")
pprint(data.to_dict())
print("ELO and NB GAMES :")
pprint(data.elo)
pprint(data.nb_games)