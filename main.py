import sys, os
import constants
import random
from player import Player, HeuristicPlayer, RandomPlayer, TruthPlayer
from board import Board
from deck import Deck
from card import Card, CardType
from repl import repl
from utils import enable_print, block_print
from typing import List, Tuple
from utils import check_win
from constants import prompt_user
from RandomPlayout import randomPlayout
from minimax import MinimaxPlayer
from tqdm import tqdm

import time


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
        enable_print()
    else:
        block_print()

    now = time.time()
    with open("eval/trevor.txt", "a+") as f:
        wins = [0,0]
        for x in tqdm(range(1)):
            # Instantiate Players
            p1 = Player("P1")
            p2 = HeuristicPlayer("P2")
            player_list = [p1, p2]
            # for x in range(num_players):
            #     # print("What is your name p{}?".format(x+1))
            #     # prompt_user()
            #     # i = input()
            #     # player_list.append(Player(i))
            #     # print()
            #     player_list.append(HeuristicPlayer("Player {}".format(x+1)))

            # Instantiate Board
            d = []
            for t in CardType:
                for _ in range(constants.NUM_COPIES):
                    d.append(Card(t))

            deck = Deck(d)
            board = Board(player_list, deck)
            winner = repl(board)

            if winner == p1:
                wins[0] +=1
            else:
                wins[1] +=1
        f.write(str(wins))
        f.write("Total Runtime : {} \n".format(time.time()-now))



