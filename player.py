from card import Card
from constants import ActionType, STARTING_MONEY, STARTING_INFLUENCE
from typing import List, Tuple


class PlayerView:
    def __init__(self):
        self.num_player = 0  # type: int
        self.deck_knowledge = {}
        self.player_claims = [] # TODO
        self.players = []  # type: List[Player]
        self.revealed = []  # type: List[Card]
        self.lost_influence = []  # type: List[Player]


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.bank = STARTING_MONEY
        self.influence = STARTING_INFLUENCE
        self.player_view = PlayerView()

    def display_hand(self):
        print("{} has the following cards:".format(self.name))
        for i in range(len(self.hand)):
            card = self.hand[i]
            print("{} - Type: {}".format(i, card.type))
    
    def display_bank(self):
        print("{} has in their bank:".format(self.name))
        print(self.bank)

    def select_action(self) -> ActionType:
        pass

    # For ambassador
    def select_cards(self, possible_cards: List[Card], number_required) -> List[Card]:
        pass

    def counteract_opponent(self, action_taken: ActionType, opposing_player) -> bool:
        pass

    def challenge_opponent(self, action_taken: ActionType, opposing_player) -> bool:
        pass

    def select_targeted_player(self, action_taken: ActionType, possible_targets: List['Player']) -> 'Player':
        pass


class RandomPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)

    def select_action(self) -> ActionType:
        if self.bank >= 10:
            return ActionType.Coup


