from board import Board, ContinuationBoard
from player import Player, RandomPlayer
from card import Card, CardType
from deck import Deck
from copy import deepcopy as copy
from repl import repl
from typing import List
from player import PlayerView
import sys
import os
import constants
import numpy as np

def randomPlayout(influence: List[int], bank : List[int], turn: int, num_playouts: int, p_view: PlayerView) -> List[float]:
    if num_playouts <= 0:
        return np.zeros(len(influence))
        
    old_out = sys.stdout
    sys.stdout = open(os.devnull, 'w')

    #Create new list of random players in same order
    taken_cards = {
        CardType.Ambassador : 0,
        CardType.Assassin : 0,
        CardType.Captain : 0,
        CardType.Contessa : 0,
        CardType.Duke : 0,
    }
    claimed_c = np.argsort(p_view.claimed_cards(p_view.players), axis=1)
    card_types = [c for c in CardType]
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

        for j in claimed_c[i]:
            if len(rp.hand) >= rp.influence:
                break
            c_type = card_types[j]
            if taken_cards[c_type] < constants.NUM_COPIES:
                rp.hand.append(Card(c_type))
                taken_cards[c_type] += 1

     #Create Deck
    d = []
    for t in CardType:
        for _ in range(constants.NUM_COPIES - taken_cards[t]):
            d.append(Card(t))
    deck = Deck(d)
    #determine number of revealed cards and discard that many
    num_revealed_cards = 2*len(influence) - sum(influence)
    deck.shuffle()
    revealed_cards = deck.draw_cards(num_revealed_cards)

    playout_board = ContinuationBoard(turn, deck, player_list, revealed_cards, lost_inf)

    wins = [0]*len(influence)
    p_names = [p.name for p in playout_board.players]
    for _ in range(num_playouts):
        winner = repl(copy(playout_board))
        w_idx = p_names.index(winner.name)
        wins[w_idx] += 1

    #Returning whether asker was the winner of random playout
    wins = np.array(wins)/num_playouts
    sys.stdout = old_out
    return wins
