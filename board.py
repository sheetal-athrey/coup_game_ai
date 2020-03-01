import constants
from player import Player
from deck import Deck
from typing import List
from card import Card

class Board():

    def _deal_starting_hand(self, player: Player):
        player.hand = self.deck.draw_cards(2)

    def end_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def display_board(self):
        print("Not Implemented - I hope you have a good memory")
    
    def display_hand(self, player: Player):
        #May display more than his hand, but not in basic version
        player.display_hand()

    def draw_card(self, player: Player):
        card = self.deck.draw_cards(1)[0]
        player.hand.append(card)

    def __init__(self, players: List[Player], deck: Deck):
        self.turn = 0
        self.deck = deck
        self.players = players

        #Deal intial hands
        for player in self.players:
            self._deal_starting_hand(player)