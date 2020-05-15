from board import Board, ContinuationBoard
from player import Player, RandomPlayer
from card import Card, CardType
from deck import Deck
from copy import deepcopy as copy
from repl import repl
from typing import List
import sys
import os
import constants
import numpy as np

def randomPlayout(influence: List[int], bank : List[int], turn: int, num_playouts: int) -> List[float]:
    if num_playouts <= 0:
        return np.zeros(len(influence))
    old_out = sys.stdout
    sys.stdout = open(os.devnull, 'w')

    wins = [0]*len(influence)
    for _ in range(num_playouts):
        #Create Deck
        d = []
        for t in CardType:
            for _ in range(constants.NUM_COPIES):
                d.append(Card(t))
        deck = Deck(d)
        #determine number of revealed cards and discard that many
        num_revealed_cards = 2*len(influence) - sum(influence)
        deck.shuffle()
        revealed_cards = deck.draw_cards(num_revealed_cards)

        #Create new list of random players in same order
        player_list = []
        lost_inf = []
        for i in range(len(influence)):
            #Random player does not use any additional info, no need to copy over anything
            #replace money and influence to match -> Also fix cards if not known
            rp = RandomPlayer("P"+str(i))
            player_list.append(rp)
            if influence[i] <= 0:
                lost_inf.append(rp)

            rp.influence = influence[i]
            rp.bank = bank[i]

            rp.hand = deck.draw_cards(rp.influence)

        playout_board = ContinuationBoard(turn, deck, player_list, revealed_cards, lost_inf)
        winner = repl(playout_board)
        w_idx = playout_board.players.index(winner)
        wins[w_idx] += 1

    #Returning whether asker was the winner of random playout
    wins = np.array(wins)/num_playouts
    sys.stdout = old_out
    return wins
