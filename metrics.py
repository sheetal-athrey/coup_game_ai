from player import Player, RandomPlayer, HeuristicPlayer
import os
import sys
from utils import create_custom_board, block_print, enable_print
from repl import repl
from logging_utils import update_json
from tqdm import tqdm
import copy
import json



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

    try:
        for i in tqdm(range(num_trials)):
            # block_print()
            print("--------------------------------------------------------", "GAME", i, "------------------------------------------------")
            print("########################################################################################################################")
            board = create_custom_board(player_configs)

            initial_cards = board.get_player_cards()
            player_types = board.get_player_types()
            winner = repl(board)

            # enable_print()

            winner_index = board.get_index_of_player(winner)

            json_update_info.append([initial_cards, winner_index, player_types])

        update_json(path_to_json, json_update_info)
    except KeyboardInterrupt:
        print("OKAY")
        board.display()






