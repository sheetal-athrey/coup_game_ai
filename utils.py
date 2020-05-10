import sys
import constants
import random
from player import Player, RandomPlayer, TruthPlayer, HeuristicPlayer
from board import Board
from deck import Deck
from card import Card, CardType
from typing import List, Tuple, Optional
import os
import json


# Disable
def block_print():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enable_print():
    sys.stdout = sys.__stdout__


def lose_card(affected_player: Player, board: Board):
    # TODO removing a card, we shouldn't reveal that it's a list underneath
    r_idx = random.randint(0, len(affected_player.hand) - 1)
    revealed_card = affected_player.hand.pop(r_idx)

    affected_player.influence -= 1
    print("{} has been revealed".format(revealed_card.type))
    board.revealed.append(revealed_card)
    if affected_player.influence == 0:
        board.lost_influence.append(affected_player)
        print("{} has lost influence".format(affected_player.name))


def check_win(players: List[Player]) -> Tuple[bool, Optional[Player]]:
    """
    Returns a tuple representing the game is over and who the winner is.

    Input:
        players - Player list - A list of players in the game

    Output:
        game_over - boolean - True if game is over, false otherwise
        winner - string - Name of the winner if game_over is true
    """
    total_players = len(players)
    for player in players:
        if player.influence == 0:
            total_players -= 1
    if total_players == 1:
        for player in players:
            if player.influence >0:
                return True, player
    return False, None


def get_alive_opponents(board: Board, player: Player) -> List[Player]:
    possible_challengers = board.players.copy()
    possible_challengers.remove(player)
    for i in board.lost_influence:
        possible_challengers.remove(i)
    return possible_challengers


def process_counter(player: Player, counter_card: Card, board: Board):
    if counter_card.type == CardType.Ambassador:
        board.update_player_actions(player, constants.RecordedActions.Block_Steal)
    elif counter_card.type == CardType.Captain:
        board.update_player_actions(player, constants.RecordedActions.Block_Steal)
    elif counter_card.type == CardType.Duke:
        board.update_player_actions(player, constants.RecordedActions.Block_Foreign_Aid)
    elif counter_card.type == CardType.Contessa:
        board.update_player_actions(player, constants.RecordedActions.Block_Assassination)


def get_initial_card_lists(list_card_names: List[List[str]]) -> List[List[Card]]:
    initial_card_lists = []
    for names in list_card_names:
        cards = []
        for name in names:
            name = name.strip()
            print(name)
            if "Ambassador" in name:
                cards.append(Card(CardType.Ambassador))
            elif "Assassin" in name:
                cards.append(Card(CardType.Assassin))
            elif "Captain" in name:
                cards.append(Card(CardType.Captain))
            elif "Contessa" in name:
                cards.append(Card(CardType.Contessa))
            elif "Duke" in name:
                cards.append(Card(CardType.Duke))
            else:
                raise Exception("Invalid Card in config file {}".format(name))
        initial_card_lists.append(cards)

    return initial_card_lists


def create_player(player_type: str, player_num: int):
    if "Random" == player_type:
        return RandomPlayer(player_num)
    elif "Truth" == player_type:
        return TruthPlayer(player_num)
    elif "Heuristic" == player_type:
        return HeuristicPlayer(player_num)
    else:
        return Player(player_num)


def create_custom_board(player_configs) -> Board:

    players = []
    player_cards = []

    # Dictionary to track remaining cards
    track_cards_remaining = {}
    for t in CardType:
        track_cards_remaining[t] = constants.NUM_COPIES

    # List for players without initial cards assigned to them.
    uninitialized_players = []

    for player_num in range(len(player_configs)):

        players.append(create_player(player_configs[player_num][0], player_num))

        if len(player_configs[player_num]) == 1:
            # Keep buffer to provide random cards later
            player_cards.append([])
            uninitialized_players.append(player_num)
        else:
            starting_cards = player_configs[player_num][1:]
            player_cards.append(starting_cards)

    # Get count of cards that have already been initialized
    initialized_card_lists = get_initial_card_lists(player_cards)

    for card_list in initialized_card_lists:
        for card in card_list:
            if track_cards_remaining[card.type] == 0:
                raise Exception("There are too many {} in the config file.".format(card.type.value))
            track_cards_remaining[card.type] -= 1

    # Create the remaining deck
    deck = []
    for t in track_cards_remaining.keys():
        for i in range(track_cards_remaining[t]):
            deck.append(Card(t))

    # Shuffle deck and randomize cards
    random.shuffle(deck)

    print("This is the list of uninitilaized players", uninitialized_players)
    dd = [i.type.value for i in deck]
    print('This is the deck', dd)
    # Give correct cards to players
    for player_num in uninitialized_players:
        player_cards[player_num] = [deck[0].type.value, deck[1].type.value]
        deck = deck[2:]

    all_initialized_card_lists = get_initial_card_lists(player_cards)
    print("ALL INITIALIZED CARD LISTS")

    board = Board(players, Deck(deck), custom=True, initial_cards=all_initialized_card_lists)

    return board










