from typing import List, Tuple
from constants import CardType


class Card:

    def __init__(self, card_type: CardType, description: str = ""):
        self.type = card_type  # type: CardType
        self.description = description # type: str

class CardType(Enum):
    Ambassador = "Ambassador"
    Assassin = "Assassin"
    Contessa = "Contessa"
    Captain = "Captain"
    Duke = "Duke"


