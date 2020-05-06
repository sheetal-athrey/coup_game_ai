from player import Player, RandomPlayer, HeuristicPlayer
import os
import sys
from constants import CardType, NUM_COPIES
from deck import Deck
from board import Board
from card import Card
from utils import create_custom_board
from repl import repl
from logging_utils import update_json



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

    for i in range(num_trials):
        board = create_custom_board(path_to_config)

        initial_cards = board.get_player_cards()
        player_types = board.get_player_types()

        winner = repl(board)

        winner_index = board.get_index_of_player(winner)

        update_json(path_to_json, initial_cards, player_types, winner_index)





