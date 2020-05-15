import sys
import constants
import random
from player import Player
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











