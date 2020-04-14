from player import Player
from deck import Deck
from typing import List


class Board:

    def _deal_starting_hand(self, player: Player):
        player.hand = self.deck.draw_cards(2)

    def end_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def display_board(self):
        print("Player's Influence:")
        for player in self.players:
            print("    {}: {}".format(player.name, player.influence))
        print()
        print("Player's Bank:")
        for player in self.players:
            print("    {}: {}".format(player.name, player.bank))
        print()
        print("Revealed Cards:")
        for card in self.revealed:
            print("    {}".format(card.type))
        print()
        print("Players who lost Influence:")
        for i in self.lost_influence:
            print("    {}".format(i.name))

    def display_hand(self, player: Player):
        # May display more than his hand, but not in basic version
        player.display_hand()

    def display_bank(self, player: Player):
        player.display_bank()

    def draw_card(self, player: Player):
        card = self.deck.draw_cards(1)[0]
        player.hand.append(card)

    def __init__(self, players: List[Player], deck: Deck):
        self.turn = 0
        self.deck = deck
        self.players = players
        self.revealed = []
        self.lost_influence = []

        # Deal initial hands
        for player in self.players:
            self._deal_starting_hand(player)