from player import Player, RandomPlayer, HeuristicPlayer, TruthPlayer
import os
import sys
from utils import block_print, enable_print
from repl import repl
from logging_utils import update_json
from tqdm import tqdm
from minimax import MinimaxPlayer
import copy
import json
from typing import List
from card import Card, CardType
from board import Board
from deck import Deck
import constants
import random


def get_initial_card_lists(list_card_names: List[List[str]]) -> List[List[Card]]:
    initial_card_lists = []
    for names in list_card_names:
        cards = []
        for name in names:
            name = name.strip()
            print(name)
            if "Ambassador" in name:
                cards.append(Card(CardType.Ambassador))
            elif "Assassin" in name:
                cards.append(Card(CardType.Assassin))
            elif "Captain" in name:
                cards.append(Card(CardType.Captain))
            elif "Contessa" in name:
                cards.append(Card(CardType.Contessa))
            elif "Duke" in name:
                cards.append(Card(CardType.Duke))
            else:
                raise Exception("Invalid Card in config file {}".format(name))
        initial_card_lists.append(cards)

    return initial_card_lists


def create_player(player_type: str, player_num: int):
    if "Random" == player_type:
        return RandomPlayer(player_num)
    elif "Truth" == player_type:
        return TruthPlayer(player_num)
    elif "Heuristic" == player_type:
        return HeuristicPlayer(player_num)
    elif "Minimax":
        return MinimaxPlayer(player_num)
    else:
        return Player(player_num)


def create_custom_board(player_configs) -> Board:

    players = []
    player_cards = []

    # Dictionary to track remaining cards
    track_cards_remaining = {}
    for t in CardType:
        track_cards_remaining[t] = constants.NUM_COPIES

    # List for players without initial cards assigned to them.
    uninitialized_players = []

    for player_num in range(len(player_configs)):

        players.append(create_player(player_configs[player_num][0], player_num))

        if len(player_configs[player_num]) == 1:
            # Keep buffer to provide random cards later
            player_cards.append([])
            uninitialized_players.append(player_num)
        else:
            starting_cards = player_configs[player_num][1:]
            player_cards.append(starting_cards)

    # Get count of cards that have already been initialized
    initialized_card_lists = get_initial_card_lists(player_cards)

    for card_list in initialized_card_lists:
        for card in card_list:
            if track_cards_remaining[card.type] == 0:
                raise Exception("There are too many {} in the config file.".format(card.type.value))
            track_cards_remaining[card.type] -= 1

    # Create the remaining deck
    deck = []
    for t in track_cards_remaining.keys():
        for i in range(track_cards_remaining[t]):
            deck.append(Card(t))

    # Shuffle deck and randomize cards
    random.shuffle(deck)

    print("This is the list of uninitilaized players", uninitialized_players)
    dd = [i.type.value for i in deck]
    print('This is the deck', dd)
    # Give correct cards to players
    for player_num in uninitialized_players:
        player_cards[player_num] = [deck[0].type.value, deck[1].type.value]
        deck = deck[2:]

    all_initialized_card_lists = get_initial_card_lists(player_cards)
    print("ALL INITIALIZED CARD LISTS")

    board = Board(players, Deck(deck), custom=True, initial_cards=all_initialized_card_lists)

    return board


if __name__ == "__main__":
    """
    input:
    [1] -- str -- path to config file
    [2] -- str -- path to json logging file
    [3] -- int -- number of trials
    """

    if len(sys.argv) < 4:
        raise Exception("Missing arguments. Require a path to configuration file and a path to json logging file.")

    path_to_config = sys.argv[1]
    path_to_json = sys.argv[2]

    if not os.path.isfile(path_to_config) or not os.path.isfile(path_to_json):
        raise Exception("Valid file paths not provided.")
    if not sys.argv[3].isnumeric():
        raise Exception("Number of trials is not valid", sys.argv[3])

    num_trials = int(sys.argv[3])

    with open(path_to_config, "r") as json_config:
        player_configs = json.load(json_config)

    json_update_info = []
    results = {}
    try:
        for i in tqdm(range(num_trials)):
            block_print()
            print("--------------------------------------------------------", "GAME", i, "------------------------------------------------")
            print("########################################################################################################################")
            board = create_custom_board(player_configs)

            initial_cards = board.get_player_cards()
            player_types = board.get_player_types()
            winner = repl(board)

            enable_print()

            winner_index = board.get_index_of_player(winner)
            print(winner_index)
            json_update_info.append([initial_cards, winner_index, player_types])

            if winner_index in results:
                results[winner_index] += 1
            else:
                results[winner_index] = 1
        enable_print()
        for idx in results.keys():
            print(idx, results[idx], player_types[idx])
        update_json(path_to_json, json_update_info)

    except KeyboardInterrupt:
        enable_print()
        print("OKAY")
        board.display()
        print(initial_cards)
        for idx in results.keys():
            print(idx, results[idx], player_types[idx])



