import random
from card import Card
from typing import List, Tuple

class Deck():
    def __init__(self, cards: List[Card]):
        self.cards = cards # type: List[Card]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw_cards(self, num_cards : int):
        """
        Returns the top num_cards of the deck

        Input:
            num_cards - int - number of cards to draw from top of the deck
        """
        cards = []
        for _ in range(num_cards):
            if len(self.cards) > 0:
                cards.append(self.cards.pop(0))
        return cards
    
    def add_bottom(self, card: Card): # TODO
        self.cards.append(card)
