from card import Card
from constants import ActionType, STARTING_MONEY, STARTING_INFLUENCE, prompt_user, CounterDecisions, CardType, clear_terminal, get_action_text, get_card_from_counter_decision, RecordedActions
from typing import List, Tuple, Optional
import numpy as np


class PlayerView:
    def __init__(self):
        self.num_player = 0  # type: int
        self.deck_knowledge = {}
        self.player_claims = {} # TODO
        self.players = []  # type: List[Player]
        self.revealed = []  # type: List[Card]
        self.lost_influence = []  # type: List[Player]

    #Returns a constants.RecordedActions x players matrix in the s
    def convert_claims(self, players: List['Player']) -> List[List[int]]:
        recorded_actions = [rec_action for rec_action in RecordedActions]
        empty = np.zeros((len(recorded_actions),len(players)))
        for i in range(len(recorded_actions)):
            ra = recorded_actions[i]
            for j in range(len(players)):
                p = players[j]
                empty[i,j] = self.player_claims[p][ra]

        return empty


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

        while True:
            prompt_user()
            input_provided = input().strip()
            if not input_provided.isnumeric():
                print("Please enter a number corresponding to an action")  # TODO the workflow here is unclear
            else:
                if self.bank >= 10:
                    return ActionType.Coup
                elif self.bank < 3 and (int(input_provided) == 4):
                    print(
                        "Not enough coins in bank for action: assassination, please pick another action")  # TODO the workflow here is unclear
                elif self.bank < 7 and (int(input_provided) == 2):
                    print(
                        "Not enough coins in bank for action: coup, please pick another action")  # TODO the workflow here is unclear
                else:
                    input_provided = int(input_provided)
                    for action in ActionType:
                        if input_provided == action.value[0] and action.value[0] <= 6:
                            return action
                    print(" A valid action was not provided")

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
        for i in range(number_required):
            selected_cards.append(possible_cards[parsed_cards[i]])

        return selected_cards

    # TODO need to combine these?
    def make_counter_decision(self, action_taken: ActionType, acting_player: 'Player') -> CounterDecisions:

        possible_counters = action_taken.value[1]
        s = "{} is trying to {}. Please make a decision on what you would like to do to counter this.\n".format(
                                            acting_player.name, get_action_text(action_taken))

        for idx, counter in enumerate(possible_counters):
            if counter == CounterDecisions.DoNothing:
                s += " {} - Do Nothing\n".format(idx)
            elif counter == CounterDecisions.Challenge:
                s += " {} - Challenge - Deny the action\n".format(idx)
            else:
                s += " {} - Counteract - By claiming {}\n".format(idx, get_card_from_counter_decision(counter))

        while True:
            print("Notice for {}:\n".format(self.name) + s)
            prompt_user()
            i = input()
            if not i.isnumeric():
                print("Please put in a numeric value")
            elif 0 <= int(i) <= len(possible_counters):
                i = int(i)
                clear_terminal()
                return possible_counters[i]
            else:
                print("Please put in a value between 0 and {}".format(len(possible_counters-1)))


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


class HeuristicPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)
        self.possible_cards = [card for card in CardType]

    def select_action(self) -> ActionType:
        #Basic Incorrect#
        if self.bank >= 10:
            return ActionType.Coup
        return ActionType.Income

    #For Ambassador
    def select_cards(self, possible_cards: List[Card], number_required) -> List[Card]:
        return possible_cards[:number_required]

    #Ror every decision basically
    def make_counter_decision(self, action_taken: ActionType, acting_player: 'Player') -> CounterDecisions:
        return CounterDecisions.DoNothing

    def select_targeted_player(self, action_taken: ActionType, possible_targets: List['Player']) -> 'Player':
        """
        Assumes action_taken in the set of (Coup, Assasinate, Steal)
        """
        if action_taken == ActionType.Steal:
            #Steal from the rich, and give to yourself - Safest move
            p_targets = np.array([player.bank for player in possible_targets])
            return possible_targets[np.argsort(p_targets)[0]]

        else:
            p_targets = np.array([player.influence for player in possible_targets])
            ca_win = .8
            d_win = .5
            as_win = .4
            co_win = .3
            am_win = .5
            not_d_win = (ca_win + as_win + co_win + am_win)/4
            not_block_steal = (as_win + co_win + d_win)/3
            not_block_as = (ca_win + d_win + co_win + am_win)/4
            block_steal = (ca_win + am_win)/2

            #Income, Foreign_aid, Coup, Tax, Assassinate, Steal, Exchange, Block_Foreign_Aid, Block_Steal, Block_Assassination, Fail_Block_Foreign, Fail_Block_Steal, Fail_Block_Assassination
            action_weights = np.array([.25 * not_d_win, 0, 0, d_win, as_win, ca_win , am_win, d_win, block_steal, co_win, not_d_win, not_block_steal, not_block_as])

            if action_taken == ActionType.Assassinate:
                action_weights[9] = action_weights[9] * -2
                action_weights[12] = action_weights[12] * 2
 
            action_weights = action_weights.reshape(1,len(action_weights))
            influence = np.array([p.influence for p in possible_targets]).reshape(len(possible_targets),1) # p -> #players

            p_weights = np.dot(influence, action_weights) #(px1) dot (1x10)
            opp_claims = self.player_view.convert_claims(possible_targets) #(10xp)
            threat_level = np.dot(p_weights, opp_claims).diagonal() # ((px10) dot (10xp)).diagonal -> (1xp)

            return possible_targets[np.argmax(threat_level)]