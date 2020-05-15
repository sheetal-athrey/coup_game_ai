from player import Player
from deck import Deck
from typing import List, Tuple, Optional
from constants import RecordedActions
from card import Card, CardType
import numpy as np
from typing import List
# import utils


class Board:

    def display(self):
        print("The turn numbers is {}".format(self.turn))
        for player in self.players:
            print(player.name, player.influence, len(player.hand), [c.type for c in player.hand])

    def _deal_starting_hand(self, player: Player):
        player.hand = self.deck.draw_cards(2)

    def _initialize_player_view(self, player: Player):
        init_claims = {}
        for p in self.players: 
            init_claims[p] = {}
            for a in RecordedActions: 
                init_claims[p][a] = 0

        player.player_view.num_player = len(self.players)
        player.player_view.player_claims = init_claims.copy()
        player.player_view.players = self.players  # Gives pointer
        player.player_view.revealed = self.revealed # Gives pointer
        player.player_view.lost_influence = self.lost_influence  # Gives pointer

    def clear_player_actions(self, player):
        for p in self.players:
            for rec_action in RecordedActions:
                p.player_view.player_claims[player][rec_action] = 0

    def update_player_actions(self, player: Player, rec_action : RecordedActions):
        for p in self.players:
            p.player_view.player_claims[player][rec_action] += 1

    def update_deck_knowledge(self, player: Player, card_pos: List[Tuple[Card,int]]):
        for card, pos in card_pos:
            player.player_view.deck_knowledge[card] = pos 

    def update_card_drawn(self, num_drawn: int):
        for player in self.players:
            deck_knowledge = player.player_view.deck_knowledge
            for card in deck_knowledge:
                new_pos = deck_knowledge[card] - 1
                if new_pos < 0:
                    del deck_knowledge[card]
                else:
                    deck_knowledge[card] = new_pos

    def end_turn(self):
        self.turn = (self.turn + 1) % len(self.players)
        self.turn_counter += 1
        # if self.turn_counter > 50:
        #     utils.enable_print()

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

    def get_index_of_player(self, player: Player):
        player_index = 0
        for p in self.players:
            if p == player:
                return player_index
            player_index += 1
        raise Exception("Invalid player provided")

    def get_player_cards(self):
        cards = []
        for p in self.players:
            player_cards = []
            for card in p.hand:
                player_cards.append(card.type.value)
            cards.append(player_cards)
        return cards

    def get_player_types(self):
        types = []
        for p in self.players:
            types.append(p.id)
        return types

    def __init__(self, players: List[Player], deck: Deck, custom: bool = False, initial_cards: Optional[List[List[Card]]]= None):
        self.turn = 0
        self.deck = deck
        self.players = players
        self.revealed = []
        self.lost_influence = []
        self.turn_counter = 0

        # Deal initial hands
        if not custom:
            for player in self.players:
                self._deal_starting_hand(player)
                self._initialize_player_view(player)
        else:
            for player, cards in zip(self.players, initial_cards):
                print([cards[0].type.value, cards[1].type.value])
                player.hand = cards
                self._initialize_player_view(player)

    def heuristic_func(self) -> List[int]:
        #super bare bones heuristic function

        card_weights = {
            CardType.Captain : .8,
            CardType.Duke : .5,
            CardType.Assassin : .4,
            CardType.Contessa : .3,
            CardType.Ambassador : .5
        }

        scores = np.zeros(len(self.players))
        for i in range(len(self.players)):
            p = self.players[i]
            if p.influence <= 0:
                score = -1
            else:
                score = 0
                score += p.influence
                hand_types = [c.type for c in p.hand]
                for t in hand_types:
                    score += card_weights[t]
                if p.bank >= 3:
                    score += .3
                elif p.bank >= 10:
                    score += .7
                elif p.bank >=7:
                    score += 1
            scores[i] = score


class ContinuationBoard(Board):
    def __init__(self, turn : int, deck : Deck, players : List[Player], revealed : List[Card], lost_i : List[Player]  ):
        self.turn = turn
        self.deck = deck
        self.players = players
        self.revealed = revealed
        self.lost_influence = lost_i
        self.turn_counter = 0
    
    #No record-keeping needed here!
    def update_player_actions(self, player: Player, rec_action : RecordedActions):
        pass

    def update_deck_knowledge(self, player: Player, card_pos: List[Tuple[Card,int]]):
        pass

    def update_card_drawn(self, num_drawn: int):
        pass
