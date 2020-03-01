import sys
import os
import constants
from player import Player
from board import Board
from deck import Deck
from card import Card, CardType

def prompt_user():
    print("> ", end="")

def check_win(players: Player):
    """
    Returns a tuple representing the game is over and who the winner is.

    Input: 
        players - Player list - A list of players in the game

    Output:
        game_over - boolean - True if game is over, false otherwise
        winner - string - Name of the winner if game_over is true
    """
    has_influence = 0
    winner = ""
    for player in players:
        if player.influence > 0:
            has_influence += 1
            winner = player.name
    return has_influence <= 1, winner

def process_input(i: str, player: Player, board: Board):
    i.strip()
    i = i.split()
    if i[0] == "help":
        print(constants.HELP_STRING)
    elif i[0] == "play":
        if not i[1].isnumeric():
            print("Please enter a number corresponding to a card in your hand")
        else:
            raise NotImplementedError
            board.end_turn()
            # idx = int(i[1])
            # if idx >=0 and idx < len(player.hand):
            #     card = player.hand[idx]
            #     player.hand.remove(card)
            #     ACTION_STACK.add_action(player=player, card=card)
            #     board.discard_card(card)
    elif i[0] == "hand":
        board.display_hand(player)
    elif i[0] == "board":
        board.display_board()
    else:
        print("Type 'help' for instructions")
    print()

def REPL(board: Board):
    """
    players - Players list - A list of player objects that represent the players.
    board - Board - a fresh board to start the game
    """
    game_over, winner = check_win(board.players)
    while not game_over:
        p_turn = board.players[board.turn]
        print("{} it is your turn".format(p_turn.name))
        prompt_user()
        i = input()
        process_input(i, p_turn, board)
        #End of action
        game_over, winner = check_win(board.players)
    
    print("{} has won the game!".format(winner))

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

    REPL(board)




    
