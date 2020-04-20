import sys
import constants
import random
from player import Player, HeuristicPlayer
from board import Board
from deck import Deck
from card import Card, CardType
from repl import repl
from typing import List, Tuple
from utils import check_win
from constants import prompt_user

if __name__ == '__main__':
    """
    input:
    [1] - int - Number of players
    """
    arg = sys.argv[1]
    if not arg.isdigit():
        print("Please put in a proper number of players")
        exit()
    num_players = int(arg)
    if num_players <= 1:
        print("There must be two or more players")
        exit()

    # Instantiate Players
    player_list = []
    for x in range(num_players):
        # print("What is your name p{}?".format(x+1))
        # prompt_user()
        # i = input()
        # player_list.append(Player(i))
        # print()
        player_list.append(HeuristicPlayer("Player {}".format(x+1)))

    # Instantiate Board
    d = []
    for t in CardType:
        for _ in range(constants.NUM_COPIES):
            d.append(Card(t))

    deck = Deck(d)
    board = Board(player_list, deck)
    repl(board)

