from player import Player
from deck import Deck
from typing import List, Tuple, Optional
from constants import RecordedActions
from card import Card


class Board:

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

        # Deal initial hands
        if not custom:
            for player in self.players:
                self._deal_starting_hand(player)
                self._initialize_player_view(player)
        else:
            for player, cards in zip(self.players, initial_cards):
                player.hand = cards
                self._initialize_player_view(player)
        for player in self.players:
            self._deal_starting_hand(player)
            self._initialize_player_view(player)


class ContinuationBoard(Board):
    def __init__(self, turn : int, deck : Deck, players : List[Player], revealed : List[Card], lost_i : List[Player]  ):
        self.turn = turn
        self.deck = deck
        self.players = players
        self.revealed = revealed
        self.lost_influence = lost_i
    
    #No recordkeeping needed here!
    def update_player_actions(self, player: Player, rec_action : RecordedActions):
        pass

    def update_deck_knowledge(self, player: Player, card_pos: List[Tuple[Card,int]]):
        pass

    def update_card_drawn(self, num_drawn: int):
        pass
