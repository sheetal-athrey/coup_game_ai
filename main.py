import sys
import os
import constants
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
    for player in players:
        if player.influence == 0:
            return True, player.name
    return False, ""


def process_input(input_string: str, player: Player, board: Board):
    input_string.strip()
    input_list = input_string.split()

    if input_list[0] == "help":
        print(constants.HELP_STRING)
    elif input_list[0] == "play":
        if not input_list[1].isnumeric():
            print("Please enter a number corresponding to an action") # TODO the workflow here is unclear
        else:
            if player.bank >= 10:
                process_action(2, player)
            else:
                process_action(int(input_list[1]), player)
    elif input_list[0] == "hand":
        board.display_hand(player)
    elif input_list[0] == "board":
        board.display_board()
    else:
        print("Type 'help' for instructions")
    print()


def repl(board: Board):
    """
    players - Players list - A list of player objects that represent the players.
    board - Board - a fresh board to start the game
    """
    game_over, winner = check_win(board.players)
    while not game_over:
        p_turn = board.players[board.turn]
        if p_turn.influence <= 0:
            board.end_turn()
        else:
            print("{} it is your turn".format(p_turn.name))
            prompt_user()
            i = input()
            process_input(i, p_turn, board)
            #End of action
            game_over, winner = check_win(board.players)
    
    print("{} has won the game!".format(winner))


def counter_action(player: Player):
    """
    Return True if action should still be carried out, False if the action does not happen
    """
    #CHECK FOR COUNTER ACTION, IF YES THEN RETURN VALUE OF CHALLENGE, OTHERWISE JUST RETURN TRUE#
    return True


def challenge(cplayer: Player, challenger: Player):
    """
    Resolve Challenge - handle challenge upkeep,
    
    Return True if action should still be carried out, False if the action does not happen
    """
    return True


def process_action(action: int, player: Player, board : Board):
    if action == 0:
        #Income#
        player.bank += 1
        board.end_turn()
    elif action == 1:
        #Foreign Aid#
        allowed = counter_action(player)
        if allowed:
            player.bank += 2
        board.end_turn()
    elif action == 2:
        print("Which player would you like to target?")
        prompt_user()



if __name__ == '__main__':
    """
    input:
    [1] - int - Number of players
    """
    arg = sys.argv[1]
    if not arg.isdigit():
        print("Please put in a proper number of players")
        exit()
    num_players = int(arg)
    if num_players <= 1:
        print("There must be two or more players")
        exit()

    #Instantiate Players
    player_list = []
    for x in range(num_players):
        print("What is your name p{}?".format(x+1))
        prompt_user()
        i = input()
        player_list.append(Player(i))
        print()

    #Instantiate Board
    d = []
    for t in CardType:
        print(t)
        for _ in range(constants.NUM_COPIES):
            d.append(Card(t))

    deck = Deck(d)
    board = Board(player_list, deck)
    repl(board)

