import csv
import TextHeadGenerator
import re
import tkinter as tk
from datetime import datetime

window = tk.Tk()
menu_frame = tk.Frame()
display_frame = tk.Frame()
menu_frame.pack(side=tk.LEFT)
display_frame.pack(side=tk.RIGHT)

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
        self.time_in_game = None

class Game:
    def __init__(self):
        self.players = []
        self.poker_log = []
        self.players_isset = False
        self.log_isset = False
        self.yourself = You()
        self.game_length = None
        self.game_start_time = None
        self.game_end_time = None

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
        self.set_game_time_stats()
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

    def set_player_quit_stats(self, player):
        play_time = None
        quit_chips = None
        for row in self.poker_log:
            if player.name in row[0] and "quit" in row[0]:
                quit_time = self.get_time_from_string(row[1])
                play_time = quit_time - self.game_start_time
                quit_chips = int((row[0].split("of "))[1].rstrip("."))
        return play_time, quit_chips

    def set_all_player_stats(self):
        for player in self.players:
            player.folds = self.set_player_folds(player)
            player.calls = self.set_player_calls(player)
            player.wins = self.set_player_wins(player)
            player.time_in_game, player.chips_quit_with = self.set_player_quit_stats(player)

    def display_player_folds(self):
        for widget in display_frame.winfo_children():
            widget.destroy()
        sorted_players = sorted(self.players, key=lambda player: player.folds, reverse=True)
        for player in sorted_players:
            list_label = tk.Label(text=player.name + ": " + str(player.folds), master=display_frame)
            list_label.pack()

    def display_player_calls(self):
        for widget in display_frame.winfo_children():
            widget.destroy()
        sorted_players = sorted(self.players, key=lambda player: player.calls, reverse=True)
        for player in sorted_players:
            list_label = tk.Label(text=player.name + ": " + str(player.calls), master=display_frame)
            list_label.pack()

    def display_player_wins(self):
        sorted_players = sorted(self.players, key=lambda player: player.wins, reverse=True)
        for player in sorted_players:
            print(player.name + ": " + str(player.wins))

    def display_player_play_time(self):
        sorted_players = sorted(self.players, key=lambda player: player.time_in_game, reverse=True)
        for player in sorted_players:
            print(player.name + ": " + str(player.time_in_game))

    def display_player_placement(self):
        players_with_chips = []
        players_without_chips = []
        placement_list = []
        #Seperate the players with and without chips to find players who split
        for player in self.players:
            if player.chips_quit_with == 0:
                players_without_chips.append(player)
            else:
                players_with_chips.append(player)
        #Make sure players with chips are the last players in the game (in case someone quit early with chips
        for player in players_with_chips:
            if player.time_in_game <= players_without_chips[0].time_in_game:
                players_without_chips.append(player)
                players_with_chips.remove(player)
        sorted_and_chipless = sorted(players_without_chips, key=lambda player: player.time_in_game, reverse=True)
        if len(players_with_chips) > 1:
            sorted_with_chips = sorted(players_with_chips, key=lambda player: player.chips_quit_with, reverse=True)
            for player in sorted_with_chips:
                placement_list.append(player.name + " split with " + str(player.chips_quit_with) + " chips")
        else:
            placement_list.append(player.name)
        for player in sorted_and_chipless:
            placement_list.append(player.name)
        for iteration, string_row in enumerate(placement_list):
            place = iteration + 1
            if place == 1:
                ordinal_indicator = "st"
            elif place == 2:
                ordinal_indicator = "nd"
            elif place == 3:
                ordinal_indicator = "rd"
            else:
                ordinal_indicator = "th"
            print(str(place) + ordinal_indicator + " - " + string_row)

    def set_game_time_stats(self):
        self.game_start_time = self.get_time_from_string(self.poker_log[-1][1])
        self.game_end_time = self.get_time_from_string(self.poker_log[1][1])
        self.game_length = self.game_end_time - self.game_start_time

    def get_time_from_string(self, time_string):
        year = re.findall("[0-9]{4}", time_string)
        month = re.findall("-([0-9]{2})-", time_string)
        day = re.findall("-([0-9]{2})T", time_string)
        hour = re.findall("T([0-9]{2}):", time_string)
        minute = re.findall(":([0-9]{2}):", time_string)
        second = re.findall(":([0-9]{2}).", time_string)
        time = datetime(int(year[0]), int(month[0]), int(day[0]), int(hour[0]), int(minute[0]), int(second[0]))
        return time

def display_window_menu():
    prompt = tk.Label(text="Please make a selection below:", master=menu_frame)
    prompt.pack()
    #button_one = tk.Button(text="List all players", master=frame, command=window_player_list(frame))
    #button_one.pack()

def window_player_list():
    for widget in display_frame.winfo_children():
        widget.destroy()
    for player in the_game.players:
        list_label = tk.Label(text=player.name, master=display_frame)
        list_label.pack()

def display_window_display(frame):
    display_label = tk.Label(text="This should be on the right side")
    display_label.pack()

def display_menu():
    print("Please choose what you would like to do:")
    print("1. List all players")
    print("2. Display folding stats")
    print("3. Exit")
    print("4. Display calling stats")
    print("5. Print poker_log")
    print("6. Display your hands")
    print("7. Display winning stats")
    print("8. Display game length")
    print("9. Display play time stats")
    print("10. Display player placement")
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
    elif selection == "8":
        print("Game length (HH:MM:SS):")
        print(the_game.game_length)
        display_menu()
    elif selection == "9":
        print("Play time stats:")
        the_game.display_player_play_time()
        display_menu()
    elif selection == "10":
        print("Player placements:")
        the_game.display_player_placement()
        display_menu()

the_game = Game()
yourself = You()
the_game.set_game_from_csv('PokerLog.csv')
yourself.set_you_from_game(the_game)
display_window_menu()
#display_window_display(display_frame)
players_btn = tk.Button(text="List all players", master=menu_frame, command=window_player_list)
folds_btn = tk.Button(text="Player Fold Stats", master=menu_frame, command=the_game.display_player_folds)
calls_btn = tk.Button(text="Player Call Stats", master=menu_frame, command=the_game.display_player_calls)
wins_btn = tk.Button(text="Player Hand Win Stats", master=menu_frame, command=the_game.display_player_wins)
playtime_btn = tk.Button(text="Player Play Time Stats", master=menu_frame, command=the_game.display_player_play_time)
players_btn.pack()
folds_btn.pack()
calls_btn.pack()
wins_btn.pack()
playtime_btn.pack()
window.mainloop()
#TextHeadGenerator.textHeadGenerator("Welcome to Poker Reader!")
#display_menu()
