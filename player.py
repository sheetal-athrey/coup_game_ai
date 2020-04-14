from card import Card
from constants import ActionType, STARTING_MONEY, STARTING_INFLUENCE
from typing import List, Tuple


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.bank = STARTING_MONEY
        self.influence = STARTING_INFLUENCE

    def display_hand(self):
        print("{} has the following cards:".format(self.name))
        for i in range(len(self.hand)):
            card = self.hand[i]
            print("{} - Type: {}".format(i, card.type))
    
    def display_bank(self):
        print("{} has in their bank:".format(self.name))
        print(self.bank)

    def select_action(self, board) -> ActionType:
        pass

    def select_cards(self, possible_cards: List[Card]) -> Tuple[List[Card], List[Card]]:
        pass

    def counteract_opponent(self, action_taken: ActionType, opposing_player) -> bool:
        pass

    def challenge_opponent(self, action_taken: ActionType, opposing_player) -> bool:
        pass


class RandomPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)

    def select_action(self, board) -> ActionType:
        if self.bank >= 10:
            return ActionType.Coup


