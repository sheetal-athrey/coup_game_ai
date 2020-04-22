import sys, os
import constants
import random
from player import Player, HeuristicPlayer, RandomPlayer
from board import Board
from deck import Deck
from card import Card, CardType
from repl import repl
from typing import List, Tuple
from utils import check_win
from constants import prompt_user

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

if __name__ == '__main__':
    """
    input:
    [1] - int - Number of players
    """
    arg = sys.argv[1]
    arg_bool = sys.argv[2] if len(sys.argv) == 3 else ""
    if not arg.isdigit():
        print("Please put in a proper number of players")
        exit()
    num_players = int(arg)
    if num_players <= 1:
        print("There must be two or more players")
        exit()
    if arg_bool == "debug":
        enablePrint()
    else:
        blockPrint()

    # Instantiate Players
    player_list = []
    for x in range(num_players):
        # print("What is your name p{}?".format(x+1))
        # prompt_user()
        # i = input()
        # player_list.append(Player(i))
        # print()
        player_list.append(RandomPlayer("Player {}".format(x+1)))

    # Instantiate Board
    d = []
    for t in CardType:
        for _ in range(constants.NUM_COPIES):
            d.append(Card(t))

    deck = Deck(d)
    board = Board(player_list, deck)
    repl(board)

