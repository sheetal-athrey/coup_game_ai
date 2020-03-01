import sys


def check_win(players: Player):
    """
    Returns a tuple representing the game is over and who the winner is.

    Input: 
        players - Player list - A list of players in the game

    Output:
        game_over - boolean - True if game is over, false otherwise
        winner - string - Name of the winner if game_over is true
    """
    for player in players:
        win = False #You can never win, ahahahahaha
        if win:
            return win, player.name
    return False, ""

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

def prompt_user():
    print("> ", end="")

def REPL(board: Board):
    """
    players - Players list - A list of player objects that represent the players.
    board - Board - a fresh board to start the game
    """
    game_over, winner = check_win(board.players)
    old_p = None
    while not game_over:
        if len(ACTION_STACK.stack) > 0:
            #ASK FOR NEIGHS HERE#
            ACTION_STACK.process_stack(board)
            #if player has only one action:
            board.end_turn()
        else:
            p_turn = board.players[board.turn]
            if old_p != p_turn:
                #process disabilities for card in player.hand {card_effect.activate(card)}#
                board.draw_card(p_turn)
            print("{} it is your turn".format(p_turn.name))
            prompt_user()
            i = input()
            process_input(i, p_turn, board)

            old_p = p_turn
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
        print("What is your name stablemasta {}?".format(x+1))
        prompt_user()
        i = input()
        player_list.append(Player(i))
        print()

    #Instantiate Board

    deck = Deck(d)
    board = Board(player_list, deck)

    REPL(board)




    
