import csv
import TextHeadGenerator
import re
import tkinter as tk
from datetime import datetime
import os

log_filename = "SampleLog.csv"
log_folder_name = "Poker Logs"
window = tk.Tk()
window.columnconfigure([0, 1], weight=1)
window.rowconfigure(1, weight=1)
header_frame = tk.Frame(master=window, height=50, relief=tk.RAISED, borderwidth=5)
view_frame = tk.Frame(master=window)
left_frame = tk.Frame(master=view_frame)
right_frame = tk.Frame(master=view_frame, pady=25, padx=25)
log_info_frame = tk.Frame(master=window)
header_frame.grid(row=0, columnspan=2, sticky="new")
view_frame.grid(row=1, columnspan=2, sticky="nsew")
left_frame.grid(row=1, column=0, columnspan=1, sticky="nsew")
right_frame.grid(row=1, column=1, sticky="nsew")
log_info_frame.grid(row=2, columnspan=2, sticky="sew")
log_info_frame.grid_rowconfigure(0, weight=1)
log_info_frame.grid_columnconfigure([0,1, 2], weight=1)

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

    def display_player_names(self, frame):
        player_list = []
        if self.players_isset == True:
            for player in self.players:
                player_list.append(player.name)
            display_stat_grid(player_list)
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

    def display_player_folds(self, frame):
        player_list = []
        folds_list = []
        sorted_players = sorted(self.players, key=lambda player: player.folds, reverse=True)
        for player in sorted_players:
            player_list.append(player.name)
            folds_list.append(player.folds)
        display_stat_grid(player_list, folds_list, grid_frame=frame)
            #iteration, string_row in enumerate(placement_list)

    def display_player_calls(self, frame):
        player_list = []
        calls_list = []
        sorted_players = sorted(self.players, key=lambda player: player.calls, reverse=True)
        for player in sorted_players:
            player_list.append(player.name)
            calls_list.append(player.calls)
        display_stat_grid(player_list, calls_list, grid_frame=frame)

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

def display_stat_grid(*stat_lists, grid_frame=right_frame, relief=tk.RAISED, border_width=2):
        for widget in grid_frame.winfo_children():
            widget.destroy()
        for column_count, column in enumerate(stat_lists):
            for row_count, data_field in enumerate(column):
                data_frame = tk.Frame(relief=relief,  width=100, borderwidth=border_width, master=grid_frame)
                data_label = tk.Label(text=data_field, master=data_frame)
                data_frame.grid(row=row_count, column=column_count, sticky="we")
                data_label.pack()

def set_csv_file(filename, csv_swap_window):
    global log_filename
    global the_game
    csv_swap_window.destroy()
    log_filename = filename
    new_game = Game()
    new_game.set_game_from_csv('Poker Logs/' + log_filename)
    the_game = new_game
    display_window_menu(menu_frame=left_frame, display_frame=right_frame, game=the_game)
    clear_stat_display()
    display_log_info()

def display_csv_swap_window():
    csv_file_list = os.listdir('Poker Logs')
    csv_swap_window = tk.Tk()
    for itr, filename in enumerate(csv_file_list):
        if ".csv" in filename:
            file_frame = tk.Frame(master=csv_swap_window, relief=tk.RIDGE, borderwidth=5)
            file_frame.grid(sticky="nsew")
            name_lbl = tk.Label(text=filename, master=file_frame)
            name_lbl.grid(row=itr, column=1, padx=20)
            select_btn = tk.Button(text="Select", master=file_frame, relief=tk.RAISED, borderwidth=5, height=2, width=8, command=lambda filename=filename: set_csv_file(filename, csv_swap_window))
            select_btn.grid(row=itr, column=0)

def display_log_info():
    for widget in log_info_frame.winfo_children():
        widget.destroy()

    label_frame = tk.Frame(master=log_info_frame, bg="red")
    selected_lbl = tk.Label(text="PokerNow Log: ", master=label_frame, relief=tk.RIDGE, borderwidth=2, height=1)
    selected_name_lbl = tk.Label(text=log_filename, master=label_frame, relief=tk.RIDGE, borderwidth=2, height=1, width=40)
    change_btn = tk.Button(text="Change", master=log_info_frame, command=display_csv_swap_window, relief=tk.RAISED, borderwidth=5, height=2, width=6, bg="green")
    label_frame.grid(sticky='swe', columnspan=2)
    selected_lbl.grid(row=0, sticky='w')
    selected_name_lbl.grid(row=0, column=1, sticky='w')
    change_btn.grid(row=0, column=2, sticky='e')

def display_window_menu(menu_frame, display_frame, game):
    for widget in menu_frame.winfo_children():
        widget.destroy()

    players_btn = tk.Button(text="List all players", master=menu_frame, command=lambda: game.display_player_names(display_frame))
    folds_btn = tk.Button(text="List Fold Stats", master=menu_frame, command=lambda: game.display_player_folds(display_frame))
    calls_btn = tk.Button(text="List Call Stats", master=menu_frame, command=lambda: game.display_player_calls(display_frame))
    wins_btn = tk.Button(text="List Hand Win Stats", master=menu_frame, command=lambda: game.display_player_wins(display_frame))
    playtime_btn = tk.Button(text="List Play Times", master=menu_frame, command=lambda: game.display_player_play_time(display_frame))
    placement_btn = tk.Button(text="List Placement", master=menu_frame, command=lambda: game.display_player_placement(display_frame))
    players_btn.grid(row=0, column=0, sticky="new", ipadx=20, ipady=10, padx=15, pady=10)
    folds_btn.grid(row=1, column=0, sticky="new", ipadx=20, ipady=10, padx=15, pady=10)
    calls_btn.grid(row=2, column=0, sticky="new", ipadx=20, ipady=10, padx=15, pady=10)
    wins_btn.grid(row=3, column=0, sticky="new", ipadx=20, ipady=10, padx=15, pady=10)
    playtime_btn.grid(row=4, column=0, sticky="new", ipadx=20, ipady=10, padx=15, pady=10)
    placement_btn.grid(row=5, column=0, sticky="new", ipadx=20, ipady=10, padx=15, pady=10)

def display_header():
    greeting = tk.Label(text="POKER READER", master=header_frame)
    greeting.pack()

def clear_stat_display():
    for widget in right_frame.winfo_children():
        widget.destroy()

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

def display_message(message, frame=right_frame):
    message = tk.Label(text=message, master=frame)
    message.grid()

the_game = Game()
yourself = You()
check_folder()
the_game.set_game_from_csv(log_folder_name + '/' + log_filename)
yourself.set_you_from_game(the_game)
display_header()
display_window_menu(menu_frame=left_frame, display_frame=right_frame, game=the_game)
display_log_info()
window.mainloop()
