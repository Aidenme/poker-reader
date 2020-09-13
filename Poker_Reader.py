import csv
import TextHeadGenerator
import re

class You:
    def __init__(self):
        self.hands = []
        self.hands_isset = False

    def set_you_from_game(self, game):
        self.hands = self.get_your_hands(game)
        self.hands_isset = True

    def get_your_hands(self, game):
        your_hands = []
        for row in game.poker_log:
            if "Your hand" in row[0]:
                reg_result = re.findall("[0-9JQKA][♦♣♥♠]|10[♦♣♥♠]", row[0])
                hand = reg_result
                your_hands.append(hand)
        return your_hands

    def display_your_hands(self):
        if self.hands_isset == True:
            for row in self.hands:
                print(row[0] + " " + row[1])
        else:
            print("Error: Your hands are not set!")

class Player:
    def __init__(self, name):
        self.name = name
        self.folds = None
        self.calls = None
        self.wins = None
        self.chips_quit_with = None
        self.quit_timecode = None

class Game:
    def __init__(self):
        self.players = []
        self.poker_log = []
        self.players_isset = False
        self.log_isset = False
        self.yourself = You()
        self.game_length = None

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
        self.set_all_player_stats()

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

    def set_player_folds(self, player):
        fold_total = 0
        for row in self.poker_log:
            if player.name in row[0] and "folds" in row[0]:
                fold_total += 1
        return fold_total

    def set_player_calls(self, player):
        calls_total = 0
        for row in self.poker_log:
            if player.name in row[0] and "calls" in row[0]:
                calls_total += 1
        return calls_total

    def set_player_wins(self, player):
        wins_total = 0
        for row in self.poker_log:
            if player.name in row[0] and "collected" in row[0]:
                wins_total += 1
        return wins_total

    def set_all_player_stats(self):
        for player in self.players:
            player.folds = self.set_player_folds(player)
            player.calls = self.set_player_calls(player)
            player.wins = self.set_player_wins(player)

    def display_player_folds(self):
        sorted_players = sorted(self.players, key=lambda player: player.folds, reverse=True)
        for player in sorted_players:
            print(player.name + ": " + str(player.folds))

    def display_player_calls(self):
        sorted_players = sorted(self.players, key=lambda player: player.calls, reverse=True)
        for player in sorted_players:
            print(player.name + ": " + str(player.calls))

    def display_player_wins(self):
        sorted_players = sorted(self.players, key=lambda player: player.wins, reverse=True)
        for player in sorted_players:
            print(player.name + ": " + str(player.wins))

def display_menu():
    print("Please choose what you would like to do:")
    print("1. List all players")
    print("2. Display folding stats")
    print("3. Exit")
    print("4. Display calling stats")
    print("5. Print poker_log")
    print("6. Display your hands")
    print("7. Display winning stats")
    selection = input()
    if selection == "1":
        the_game.print_player_names()
        display_menu()
    elif selection == "2":
        print("Player fold stats:")
        the_game.display_player_folds()
        display_menu()
    elif selection == "3":
        exit()
    elif selection == "4":
        print("Player call stats:")
        the_game.display_player_calls()
        display_menu()
    elif selection == "5":
        the_game.print_poker_log()
        display_menu()
    elif selection == "6":
        yourself.display_your_hands()
        display_menu()
    elif selection == "7":
        print("Player hand wins:")
        the_game.display_player_wins()
        display_menu()

the_game = Game()
yourself = You()
the_game.set_game_from_csv('PokerLog.csv')
yourself.set_you_from_game(the_game)
TextHeadGenerator.textHeadGenerator("Welcome to Poker Reader!")
display_menu()
