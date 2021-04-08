import csv
import TextHeadGenerator
import re
import tkinter as tk
from datetime import datetime
import os

log_filename = "SampleLog.csv"
log_folder_name = "Poker Logs"

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
        try:
            with open(csv_file) as csvfile:
                poker_log_reader = csv.reader(csvfile, delimiter=',')
                for row in poker_log_reader:
                    self.poker_log.append(row)
        except:
            print("Could not find CSV file in Poker Logs folder.")
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

    def display_player_names(self):
        player_list = []
        if self.players_isset == True:
            for player in self.players:
                print(player.name)
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
        did_player_quit = False
        for row in self.poker_log:
            if player.name in row[0] and "quit" in row[0]:
                quit_time = self.get_time_from_string(row[1])
                play_time = quit_time - self.game_start_time
                quit_chips = int((row[0].split("of "))[1].rstrip("."))
                did_player_quit = True
        # If all players quit the last player will not have "quit" in any row of the log.
        if did_player_quit == False:
            play_time = self.game_length
            quit_chips = len(self.players) * 300

        return play_time, quit_chips

    def set_all_player_stats(self):
        for player in self.players:
            player.folds = self.set_player_folds(player)
            player.calls = self.set_player_calls(player)
            player.wins = self.set_player_wins(player)
            player.time_in_game, player.chips_quit_with = self.set_player_quit_stats(player)

    def display_player_folds(self):
        player_list = []
        folds_list = []
        sorted_players = sorted(self.players, key=lambda player: player.folds, reverse=True)
        for player in sorted_players:
            print(str(player.name) + " " + str(player.folds))

    def display_player_calls(self):
        player_list = []
        calls_list = []
        sorted_players = sorted(self.players, key=lambda player: player.calls, reverse=True)
        for player in sorted_players:
            print(player.name + " " + str(player.calls))

    def display_player_wins(self, frame):
        player_list = []
        wins_list = []
        sorted_players = sorted(self.players, key=lambda player: player.wins, reverse=True)
        for player in sorted_players:
            player_list.append(player.name)
            wins_list.append(player.wins)
        display_stat_grid(player_list, wins_list, grid_frame=frame)

    def display_player_play_time(self, frame):
        player_list = []
        play_time_list = []

        sorted_players = sorted(self.players, key=lambda player: player.time_in_game, reverse=True)
        for player in sorted_players:
            player_list.append(player.name)
            play_time_list.append(player.time_in_game)
        display_stat_grid(player_list, play_time_list, grid_frame=frame)

    def display_player_placement(self, frame):
        player_list = []
        chips_list = []
        placement_string_list = []
        for widget in frame.winfo_children():
            widget.destroy()
        players_with_chips = []
        players_without_chips = []
        placement_list = []
        #Seperate the players with and without chips to find players who split
        for player in self.players:
            if player.chips_quit_with == 0:
                players_without_chips.append(player)
            else:
                players_with_chips.append(player)
        #Make sure players with chips are the last players in the game (in case someone quit early with chips)
        for player in players_with_chips:
            if player.time_in_game <= players_without_chips[0].time_in_game:
                players_without_chips.append(player)
                players_with_chips.remove(player)
        sorted_and_chipless = sorted(players_without_chips, key=lambda player: player.time_in_game, reverse=True)
        if len(players_with_chips) > 1:
            sorted_with_chips = sorted(players_with_chips, key=lambda player: player.chips_quit_with, reverse=True)
            for player in sorted_with_chips:
                placement_list.append(player.name)
                chips_list.append("SPLIT: " + str(player.chips_quit_with) + " chips")
        else:
            placement_list.append(player.name)
            chips_list.append("WINNER")
        for player in sorted_and_chipless:
            placement_list.append(player.name)
            chips_list.append("KO")
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
            placement_string_list.append(str(place) + ordinal_indicator)
        display_stat_grid(placement_string_list, placement_list, chips_list, grid_frame=frame)

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

def check_for_logs():
    file_list = os.listdir(log_folder_name)
    print(file_list)
    any_csv = False
    for row in file_list:
        if ".csv" in row:
            any_csv = True
    if any_csv == False:
        display_message("No PokerNow logs found in " + log_folder_name + " folder. Please put a CSV file in the folder.")

def check_folder():
    directory_list = os.listdir()
    if log_folder_name not in directory_list:
        os.mkdir(log_folder_name)
    check_for_logs()

the_game = Game()
yourself = You()
check_folder()
the_game.set_game_from_csv(log_folder_name + '/' + log_filename)
yourself.set_you_from_game(the_game)
the_game.display_player_calls()
