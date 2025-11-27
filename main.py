from data import *
from loaders import *

loader = DataLoader()
data = Data()
file_path = "import_files/04_10_2025 16_45.csv"
loader.load_game_csv(data, file_path)