import csv
import TextHeadGenerator
import re

#Hands won
#Track 1v1s and who wins with what
#Heads up counter. That's basically 1st and 2nd place winners
#Types of hands won on. I want to know what everyone wins on.

poker_log = []
players = []
player_stats = []
you = {}

def csv_to_poker_log():
    with open('PokerLog.csv') as csvfile:
        poker_log_reader = csv.reader(csvfile, delimiter=',')
        for row in poker_log_reader:
            poker_log.append(row)

def print_poker_log():
    for row in poker_log:
        print(row)

def set_players_list():
    #Split the last row in the log
    split_row = poker_log[len(poker_log) - 1][0].split()
    players.append(split_row[2].strip('"'))
    #Add the other players to the list
    for row in poker_log:
        if row[0].startswith("The admin approved the player"):
            split_row = row[0].split()
            players.append(split_row[5].strip('"'))
    #for row in poker_log:
    #    if row[0] == '"The' and row[1] == "admin" and row[2] == "approved":
    #        players.append(row[5].strip('"'))

def print_players():
    print("Players in game:")
    for row in players:
        print(row)

def get_player_folds(player):
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

def set_player_stats():
    for player in players:
        player_stats.append({
            "name" : player,
            "folds" : get_player_folds(player),
            "calls" : get_player_calls(player)
        })

def set_your_stats():
    you["hands"] = get_your_hands()



def display_player_stat(stat):
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
    selection = input()
    if selection == "1":
        print_players()
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


csv_to_poker_log()
set_players_list()
set_player_stats()
set_your_stats()
TextHeadGenerator.textHeadGenerator("Welcome to Poker Reader!")
display_menu()
print(you)
