import sys
import constants
import random
from player import Player
from board import Board
from deck import Deck
from card import Card, CardType
from typing import List, Tuple


def prompt_user():
    print("> ", end="")


def check_win(players: List[Player]) -> Tuple[bool, str]:
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
                return True, player.name
    return False, ""


def get_alive_opponents(board: Board, player: Player) -> List[Player]:
    possible_challengers = board.players.copy()
    possible_challengers.remove(player)
    for i in board.lost_influence:
        possible_challengers.remove(i)
    return possible_challengers

def process_counter(player: Player, counter_card: Card, board: Board):
    if counter_card.type == CardType.Ambassador:
        board.update_player_actions(player, RecordedActions.Block_Steal)
    elif counter_card.type == CardType.Captain:
        board.update_player_actions(player, RecordedActions.Block_Steal)
    elif counter_card.type == CardType.Duke:
        board.update_player_actions(player, RecordedActions.Block_Foreign_Aid)
    elif counter_card.type == CardType.Contessa:
        board.update_player_actions(player, RecordedActions.Block_Assassination)

