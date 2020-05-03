from board import Board, ContinuationBoard
from player import Player, RandomPlayer
from card import Card, CardType
from deck import Deck
from copy import deepcopy as copy
from repl import repl
import sys
import os

def randomPlayout(board: Board, turn: int, asker: Player) -> bool:
    old_out = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    a_idx = board.players.index(asker)

    #Dont know people's cards so put them back in the deck, will deal out randomly later
    deck = copy(board.deck)
    for p in board.players:
        if not p == asker:
            for card in p.hand:
                deck.add_bottom(card)
    deck.shuffle()

    #Create new list of random players in same order
    player_list = []
    lost_inf = []
    for p in board.players:
        #Random player does not use any additional info, no need to copy over anything
        #replace money and influence to match -> Also fix cards if not known
        rp = RandomPlayer(p.name)
        player_list.append(rp)
        if p.influence <= 0:
            lost_inf.append(rp)

        rp.influence = p.influence
        rp.bank = p.bank

        if p == asker:
            rp.hand = p.hand.copy()
        else:
            rp.hand = deck.draw_cards(rp.influence)

    playout_board = ContinuationBoard(turn, deck, player_list, board.revealed.copy(), lost_inf)
    winner = repl(playout_board)
    w_idx = playout_board.players.index(winner)

    #Returning whether asker was the winner of random playout
    sys.stdout = old_out
    print("winner of random playout: {}".format(winner.name))
    return a_idx == w_idx
