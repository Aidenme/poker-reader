import csv
import TextHeadGenerator
import re

poker_log = []
player_stats = []
you = {}

class Player:
    def __init__(self, name):
        self.name = name
        self.folds = 0
        self.calls = 0
        self.wins = 0

class Game:
    def __init__(self):
        self.players = []
        self.poker_log =[]
        self.players_isset = False
        self.log_isset = False

    def set_players(self):
        player_names = []
        #Split the last row in the log
        split_row = self.poker_log[len(self.poker_log) - 1][0].split()
        #Add the admin to the list
        name = split_row[2].strip('"')
        self.players.append(Player(name))
        player_names.append(name)
        #Add the other players to the list
        for row in self.poker_log:
            if row[0].startswith("The admin approved the player"):
                split_row = row[0].split()
                name = split_row[5].strip('"')
                #Handling duplicates (like if a game restarts)
                if name not in player_names:
                    self.players.append(Player(name))
                    player_names.append(name)
        self.players_isset = True

    def set_game_from_csv(self, csv_file):
        with open(csv_file) as csvfile:
            poker_log_reader = csv.reader(csvfile, delimiter=',')
            for row in poker_log_reader:
                self.poker_log.append(row)
        self.log_isset = True
        self.set_players()

    def print_poker_log(self):
        if self.log_isset == True:
            for row in self.poker_log:
                print(row)
        else:
            print("Error: poker_log is not set!")

    def print_player_names(self):
        if self.players_isset == True:
            for row in self.players:
                print(row.name)
        else:
            print("Error: players are not set!")

    def get_player_folds(self, player_name):
        fold_total = 0
        for row in self.poker_log:
            if player_name in row[0] and "folds" in row[0]:
                fold_total += 1
        return fold_total

def get_player_folds(game, player):
    fold_total = 0
    for row in poker_log:
        if player in row[0] and "folds" in row[0]:
            fold_total += 1
    return fold_total

def get_player_calls(player):
    calls_total = 0
    for row in poker_log:
        if player in row[0] and "calls" in row[0]:
            calls_total += 1
    return calls_total

def get_player_wins(player):
    wins_total = 0
    for row in poker_log:
        if player in row[0] and "collected" in row[0]:
            wins_total += 1
    return wins_total

def set_player_stats(game):
    for player in game.players:
        player.folds = 10
        player.calls = 10
        player.wins = 10

def set_your_stats():
    you["hands"] = get_your_hands()

def display_player_stats(stat):
    folds_display = []

    def take_key_value(key):
        return key.get(stat)

    folds_display = sorted(player_stats, key=take_key_value, reverse=True)

    for row in folds_display:
        print(row.get("name") + ": " + str(row.get(stat)))

def get_your_hands():
    your_hands = []
    for row in poker_log:
        if "Your hand" in row[0]:
            reg_result = re.findall("[0-9JQKA][♦♣♥♠]|10[♦♣♥♠]", row[0])
            hand = reg_result
            your_hands.append(hand)
    return your_hands

def display_your_hands():
    for row in you["hands"]:
        print(row[0] + " " + row[1])

def display_menu():
    print("Please choose what you would like to do:")
    print("1. List all players")
    print("2. Display folding stats")
    print("3. Exit")
    print("4. Display calling stats")
    print("5. Print poker_log")
    print("6. Get your hands")
    print("7. Get winning stats")
    selection = input()
    if selection == "1":
        the_game.print_player_names()
        display_menu()
    elif selection == "2":
        print("Player fold stats:")
        display_player_stat("folds")
        display_menu()
    elif selection == "3":
        exit()
    elif selection == "4":
        print("Player call stats:")
        display_player_stat("calls")
        display_menu()
    elif selection == "5":
        print_poker_log()
        display_menu()
    elif selection == "6":
        display_your_hands()
        display_menu()
    elif selection == "7":
        display_player_stat("wins")
        display_menu()

the_game = Game()
the_game.set_game_from_csv('PokerLog.csv')
#set_players_list()
#set_player_stats()
set_your_stats()
TextHeadGenerator.textHeadGenerator("Welcome to Poker Reader!")
display_menu()
