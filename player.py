from card import Card
from constants import ActionType, STARTING_MONEY, STARTING_INFLUENCE
from typing import List, Tuple
from repl import prompt_user


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
    # Returns list of cards selected.
    def select_cards(self, possible_cards: List[Card], number_required) -> List[Card]:
        # Display cards
        for card_index in range(len(possible_cards)):
            print(str(card_index) + ": " + str(possible_cards[card_index].type))
        print("Please select {} card(s) by typing numbers spaced apart into the prompt. "
              "If a valid input is not provided then you will keep your current cards".format(self.influence))

        prompt_user()
        index_selected = input()

        # Determine cards selected
        parsed_cards = index_selected.split(" ")
        parsed_cards = [int(i) for i in parsed_cards]

        selected_cards = []
        for i in range(self.influence):
            selected_cards.append(possible_cards[parsed_cards[i]])

        return selected_cards

    def counteract_opponent(self, action_taken: ActionType, opposing_player) -> bool:
        pass

    def challenge_opponent(self, action_taken: ActionType, opposing_player) -> bool:
        pass

    def select_targeted_player(self, action_taken: ActionType, possible_targets: List['Player']) -> 'Player':
        s = "Notice for {}:\n Return in numeric value which player you would like to target.\n".format(self.name)

        for idx, i in enumerate(possible_targets):
            s += "{} : {} \n".format(idx, i.name)
        print(s)
        not_answered = True
        while not_answered:
            prompt_user()
            i = input()
            if not i.isnumeric():
                print("Please put in a numeric value")
            elif 0 <= int(i) <= len(possible_targets):
                return possible_targets[int(i)]
            else:
                print("Please put in a value between 0 and {}".format(len(possible_targets)))


class RandomPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)

    def select_action(self) -> ActionType:
        if self.bank >= 10:
            return ActionType.Coup


