# Utils for printing and such

def print_freqs(freq):
    winds = ['East', 'South', 'West', 'North', 'Total']
    places = ['1st', '2nd', '3rd', '4th']
    for wind in range(len(winds)):
        print(f"\t{winds[wind]} : ", end="")
        for place in range(len(places)):
            if place != 0: print(", ", end="")
            print(f"{places[place]} : {freq[wind][place][0]} ({round(100*freq[wind][place][1], 1)}%)", end="")
        print()

def print_counts(count):
    nb_prints = 0
    for p, val in dict(sorted(count.items(), key=lambda x: x[1], reverse=True)).items():
        if val > 0:
            print(f"\t{p} : {val}", end="\t")
            nb_prints += 1
            if nb_prints%4 == 0:
                print()
    if nb_prints%4 != 0: print()

def print_nemesis(stat):
    nb_prints = 0
    for p, val in dict(sorted(stat.items(), key=lambda x: (x[1]['smoothed_rate'], x[1]['win_rate'], -x[1]['nb_total']), reverse=False)).items():
        if val['nb_total'] > 0:
            print(f"\t{p} : {val['nb_wins']:.0f}/{val['nb_total']:.0f} ({100 * val['win_rate']:.1f}%)", end="\t")
            nb_prints += 1
            if nb_prints%3 == 0:
                print()
    if nb_prints%4 != 0: print()

def print_game(data, game, detail=None):
    print(str(game.date) + " : " + " / ".join([data.aliases[name] for name in game.players]))
    if detail is not None:
        names = list(detail["elo_before"].keys())
        print("\tNom\t\tPlace\t\tElo diff\tPoints attendus\tElo avant\tElo gain\tElo apres")
        for name in names:
            print(f"\t{name + ("\t" if len(name) < 8 else "")}\t", end="")
            place = detail["place"][name]
            print(f"{str(place) + ("er" if place == 1 else "e")}\t\t", end="")
            print(f"{detail["elo_diff"][name]:.1f}\t\t{detail["awaited_perf"][name]:.2f}\t\t{detail["elo_before"][name]:.1f}\t\t{detail["elo_gain"][name]:.1f}\t\t{detail["elo_after"][name]:.1f}")
        print()