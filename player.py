from card import Card
from constants import ActionType, STARTING_MONEY, STARTING_INFLUENCE, prompt_user, CounterDecisions, CardType, clear_terminal, get_action_text, get_card_from_counter_decision, RecordedActions
from typing import List, Tuple, Optional
import numpy as np
import random


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

    def claimed_cards(self, players: List['Player']) -> List[List[int]]:
        card_types = [typ for typ in CardType]
        claim_conversion = { #Ambassador(0), Assassin(1), Contessa(2), Captain(3), Duke(4) -> With respect to card types
            0 : [(4, -.25)],
            1 : [(4, -.25)],
            2 : [(0,0)],
            3 : [(4, 1)],
            4 : [(1, 1)],
            5 : [(3, 1)],
            6 : [(0, 1)],
            7 : [(4, 1)],
            8 : [(0, 1), (3, 1)],
            9 : [(2, 1)],
            10 : [(4, -.5)],
            11 : [(0, -1), (3, -1)],
            12 : [(2, -1.5)]
        }
        claims = self.convert_claims(players)
        card_claims = np.zeros((len(players), len(card_types)))
        for i in range(len(claims[0])): #p
            for j in range(len(claims)): #13 
                for pos, weight in claim_conversion[j]:
                    card_claims[i, pos] += weight * claims[j, i]
        
        return card_claims #p x cards
    
    def can_FA(self, players: List['Player']) -> bool:
        for p in players:
           if self.player_claims[p][RecordedActions.Block_Foreign_Aid] > 1:
               return False
        return True

    def can_Steal(self, players: List['Player']) -> List['Player']:
        can = players.copy()
        for p in players:
            if self.player_claims[p][RecordedActions.Block_Steal] > 1:
               can.remove(p)
        return can
    
    def can_Assassinate(self, players: List['Players']) -> List['Player']:
        can = players.copy()
        for p in players:
           if self.player_claims[p][RecordedActions.Block_Assassination] > 1:
               can.remove(p)
        return can


class Player:
    def __init__(self, name: str):
        self.id = "Human"
        self.name = name
        self.hand = []
        self.bank = STARTING_MONEY
        self.influence = STARTING_INFLUENCE
        self.player_view = PlayerView()

    def display_hand(self):
        print("{} has the following cards:".format(self.name))
        print(self.hand)
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
        self.id = "Random"

    def select_action(self) -> ActionType:
        possible_actions = [e for e in ActionType if e.value[0]<7]
        if self.bank >= 10:
            return ActionType.Coup
        else:
            if self.bank < 7:
                possible_actions.remove(ActionType.Coup)
                if self.bank < 3:
                    possible_actions.remove(ActionType.Assassinate)
        return random.choice(possible_actions)
    

    def select_cards(self, possible_cards: List[Card], number_required) -> List[Card]:
        return random.choices(possible_cards, k=2)


    # TODO need to combine these?
    def make_counter_decision(self, action_taken: ActionType, acting_player: 'Player') -> CounterDecisions:
        print(action_taken)
        possible_counters = action_taken.value[1]
        chosen = random.choice(possible_counters)
        print(chosen)
        return chosen


    def select_targeted_player(self, action_taken: ActionType, possible_targets: List['Player']) -> 'Player':
        return random.choice(possible_targets)


class TruthPlayer(RandomPlayer):
    def select_action(self) -> ActionType:
        associations = {
            CardType.Ambassador : ActionType.Exchange,
            CardType.Captain : ActionType.Steal,
            CardType.Duke : ActionType.Tax
        }
        if self.bank >= 10:
            return ActionType.Coup
        possible_actions = [ActionType.Income, ActionType.Foreign_aid]
        if self.bank >= 7:
            possible_actions.append(ActionType.Coup)
        hand_types = [c.type for c in self.hand]
        if self.bank >= 3 and CardType.Assassin in hand_types:
            possible_actions.append(ActionType.Assassinate)
        for t in hand_types:
            if t in associations:
                possible_actions.append(associations[t])
        return random.choice(possible_actions)
    
    def make_counter_decision(self, action_taken: ActionType, acting_player: 'Player') -> CounterDecisions:
        counter_association ={
            CounterDecisions.BlockForeignAid : CardType.Duke,
            CounterDecisions.BlockStealingAmbassador : CardType.Ambassador,
            CounterDecisions.BlockStealingCaptain : CardType.Captain,
            CounterDecisions.BlockAssassination : CardType.Contessa,
        }
        print(action_taken)
        hand_types = [c.type for c in self.hand]
        possible_counters = action_taken.value[1]
        allowed_counters = []
        for counter in possible_counters:
            if counter in counter_association:
                if counter_association[counter] in hand_types:
                    allowed_counters.append(counter)
            else:
                allowed_counters.append(counter)
        chosen = random.choice(possible_counters)
        print(chosen)
        return chosen


class HeuristicPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)
        self.id = "Heuristic"
        self.possible_cards = [card for card in CardType]
        self.card_confidence = {
            CardType.Captain : .8,
            CardType.Duke : .5,
            CardType.Assassin : .4,
            CardType.Contessa : .3,
            CardType.Ambassador : .5,
        }

    def select_action(self) -> ActionType:
        #Basic Incorrect#
        if self.bank >= 7:
            return ActionType.Coup
        card_types = [card for card in CardType]
        opp_think = self.player_view.claimed_cards([self])

        thought_types = []
        print("opp thinks I am: {}".format(opp_think[0]))
        # if np.allclose(opp_think[0], np.zeros(len(opp_think[0]))): 
        #     return ActionType.Foreign_aid
        # else: 
        for c_idx in (np.argsort(opp_think[0])[::-1])[:self.influence]:
            if opp_think[0][c_idx] != 0:
                thought_types.append(card_types[c_idx])
        
        thought_types = set(thought_types)
        hand_types = [card.type for card in self.hand]

        opponents = list(filter(lambda p : p.influence > 0 and p != self, self.player_view.players))
        can_steal = len(self.player_view.can_Steal(opponents)) > 0
        can_assassinate = len(self.player_view.can_Assassinate(opponents)) > 0
        can_fa = self.player_view.can_FA(opponents)
        
        if self.influence == 1:
            if CardType.Assassin in hand_types and self.bank >= 3 and can_assassinate:
                return ActionType.Assassinate
            elif CardType.Duke in hand_types:
                return ActionType.Tax
            elif (not CardType.Captain in hand_types):
                return ActionType.Exchange
            elif can_steal:
                return ActionType.Steal
        else: 
            if CardType.Assassin in thought_types and self.bank >= 3 and can_assassinate:
                return ActionType.Assassinate
            elif len(thought_types.intersection(set(hand_types))) == len(self.hand):
                return ActionType.Exchange
            elif CardType.Captain in thought_types and can_steal :
                return ActionType.Steal
            elif CardType.Duke in thought_types:
                return ActionType.Tax
            
        if can_fa:
            return ActionType.Foreign_aid   
        return ActionType.Income

    #For Ambassador
    def select_cards(self, possible_cards: List[Card], number_required) -> List[Card]:
        choice_types = [card.type for card in possible_cards]
        card_types = [typ for typ in CardType]
        if number_required == 2:
            opponents = list(filter(lambda p : p.influence > 0 and p != self, self.player_view.players))
            opponent_claim_cards = self.player_view.claimed_cards(opponents) # p x c
            total_claims = np.sum(opponent_claim_cards, axis = 0)

            most_rel_opp_cards = np.argsort(total_claims)[::-1]

            wanted_cards = []
            for rel_card_idx in most_rel_opp_cards:
                if card_types[rel_card_idx] == CardType.Ambassador:
                    wanted = CardType.Ambassador
                elif card_types[rel_card_idx] == CardType.Assassin:
                    wanted = CardType.Contessa
                elif card_types[rel_card_idx] == CardType.Captain:
                    wanted = CardType.Captain
                elif card_types[rel_card_idx] == CardType.Contessa:
                    wanted = CardType.Duke
                elif card_types[rel_card_idx] == CardType.Duke:
                    wanted = CardType.Assassin

                wanted_cards.append(possible_cards[choice_types.index(wanted)]) if wanted in choice_types else 1

                if len(wanted_cards) == number_required:
                    return wanted_cards
                    
        elif number_required == 1:
            if CardType.Captain in choice_types:
                return [possible_cards[choice_types.index(CardType.Captain)]]
            elif CardType.Ambassador in choice_types:
                return [possible_cards[choice_types.index(CardType.Ambassador)]]
            elif CardType.Duke in choice_types:
                return [possible_cards[choice_types.index(CardType.Duke)]]
            elif CardType.Ambassador in choice_types:
                return [possible_cards[choice_types.index(CardType.Ambassador)]]
            elif CardType.Assassin in choice_types:
                return [possible_cards[choice_types.index(CardType.Assassin)]]
            elif CardType.Contessa in choice_types:
                return [possible_cards[choice_types.index(CardType.Contessa)]]

    #Ror every decision basically
    def make_counter_decision(self, action_taken: ActionType, acting_player: 'Player') -> CounterDecisions:
        #defining helpful info
        card_types = [typ for typ in CardType]
        action_to_card_idx = {
            ActionType.Foreign_aid : [4], 
            ActionType.Tax : [4] ,
            ActionType.Assassinate : [1],
            ActionType.Steal : [0,2], 
            ActionType.Exchange : [0],
            ActionType.Block_Foreign_Aid : [4],
            ActionType.Block_Steal_Ambassador : [0],
            ActionType.Block_Steal_Captain : [2], 
            ActionType.Block_Assassination : [3],
        }

        #create one-hot representation of choices
        all_counters = [counter for counter in CounterDecisions]
        possible_counters = action_taken.value[1]
        one_hot_p_counters = [1 if counter in possible_counters else 0 for counter in all_counters]

        #Set base confidence threshold that must be exceeded to anything but nothing.
        if self.influence == 2:
            threshold = .5
        else:
            threshold = self.card_confidence[self.hand[0].type]

        #Define base weights based off of what the opponent thinks of us
        opp_thinks = []
        card_types = [t for t in CardType]
        opp_view = self.player_view.claimed_cards([self])[0]
        for x in (np.argsort(opp_view)[::-1])[:2]:
            if opp_view[x] > 0:
                opp_thinks.append(card_types[x])

        opp_cards = self.player_view.claimed_cards([acting_player])
        if action_taken == ActionType.Steal:
            challenge = (opp_cards[0][0] + opp_cards[0][2])/2
        else:
            challenge = opp_cards[0][action_to_card_idx[action_taken][0]]
            s = np.sum(opp_cards)
            if s < 0: 
                challenge = .5 + opp_cards[0][action_to_card_idx[action_taken][0]] / s
            elif s > 0:
                challenge = .5 - opp_cards[0][action_to_card_idx[action_taken][0]] / s #challenge/sum = % of claim associated with that card
            else: 
                challenge = 0
        opp_thinks_duke = 1 if CardType.Duke in opp_thinks else 0
        opp_thinks_cont = 1 if CardType.Contessa in opp_thinks else 0
        opp_thinks_assa = 1 if CardType.Assassin in opp_thinks else 0
        opp_thinks_cap = 1 if CardType.Captain in opp_thinks else 0

        weights = [threshold, challenge, opp_thinks_duke, opp_thinks_cont, opp_thinks_assa, opp_thinks_cap]

        #finally factor in all known cards -> to opponents the cards you know in the deck are
        #indistinguishable from the ones in your hand (with minor exceptions but who needs to think bout that)

        known_cards = self.hand + list(self.player_view.deck_knowledge.keys())

        inv_influence = 3 - self.influence
        for card in known_cards:
            c_idx = card_types.index(card.type)
            if card.type == CardType.Ambassador:
                weights[4] += .33 * inv_influence
            elif card.type == CardType.Captain:
                weights[5] += .33 * inv_influence
            elif card.type == CardType.Contessa:
                weights[3] += 1
            elif card.type == CardType.Duke:
                weights[2] += .33 * inv_influence
            
            if c_idx in action_to_card_idx[action_taken]:
                weights[1] += .167 * inv_influence
        
        decision_scores = np.multiply(one_hot_p_counters, weights)
        print("decision scores: {}".format(decision_scores))
        return all_counters[np.argmax(decision_scores)]

    def select_targeted_player(self, action_taken: ActionType, possible_targets: List['Player']) -> 'Player':
        """
        Assumes action_taken in the set of (Coup, Assasinate, Steal)
        """
        if action_taken == ActionType.Steal:
            #Steal from the rich, and give to yourself - Safest move
            possible_targets = self.player_view.can_Steal(possible_targets)
            p_targets = np.array([player.bank for player in possible_targets])
            return possible_targets[(np.argsort(p_targets)[::-1])[0]]

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