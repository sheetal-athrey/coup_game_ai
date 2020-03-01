from typing import List, Tuple
from enum import Enum


class CardType(Enum):
    Ambassador = "Ambassador"
    Assassin = "Assassin"
    Contessa = "Contessa"
    Captain = "Captain"
    Duke = "Duke"

class Card:

    def __init__(self, card_type: CardType, description: str = ""):
        self.type = card_type  # type: CardType
        self.description = description # type: str


