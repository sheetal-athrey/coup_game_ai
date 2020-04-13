import sys
import os
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
                process_action(2, player, board)
            elif player.bank < 3 and (int(input_list[1])== 4) :
                print("Not enough coins in bank for action: assassination, please pick another action") # TODO the workflow here is unclear
            elif player.bank < 7 and (int(input_list[1])== 2) :
                print("Not enough coins in bank for action: coup, please pick another action") # TODO the workflow here is unclear
            else:
                process_action(int(input_list[1]), player, board)
    elif input_list[0] == "hand":
        board.display_hand(player)
    elif input_list[0] == "board":
        board.display_board()
    elif input_list[0] == "bank":
        board.display_bank(player)
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


def counter_action(player: Player, cPlayers: List[Player], action: str, counterCards : List[CardType], board: Board, against_claim: bool = False):
    """
    Return True if action should still be carried out, False if the action does not happen
    """
    #Format string to ask players#
    challengers = []
    s = "{} is trying to {}, would you like to counteract this action?\n Please type one of the following choices:\n 0 - Do nothing\n".format(player.name, action)
    for idx, card in enumerate(counterCards):
        if not against_claim:
            s += " {} - Counter - Claim to have {}\n".format(idx+1, card) 
        else:
            s += " {} - Counter - Deny {} claim to having a {}\n".format(idx+1, player.name+"\'s",card)   

    #Loop through possible players and see if they would like to invoke a counteraction#
    for p in cPlayers:
        not_answered = True
        while not_answered:
            print("Notice for {}:\n".format(p.name) + s)
            prompt_user()
            i = input()
            if not i.isnumeric():
                print("Please put in a numeric value")
            elif int(i) >= 0 and int(i) <= len(counterCards):
                i = int(i)
                if i == 0: 
                    challengers.append((p,False,None))
                else:
                    i -= 1
                    challengers.append((p, True, counterCards[i]))
                not_answered = False
            else:
                print("Please put in a value between 0 and {}".format(len(counterCards)))
        constants.clear_terminal()
        print("just past clear")
    
    #PseudoRandom way of representing people speaking out of turn#
    random.shuffle(challengers)

    #Check if anyone chose to invoke a counter action and determine if the initial player would like to challenge the counteraction#
    if not against_claim:
        for (cPlayer,chal,card) in challengers:
            if chal:
                not_answered = True
                while not_answered:
                    print("""Notice for {}:\n{} is counteracting your action by claiming to have {}.\nWould you like to challenge this? y/n""".format(player.name, cPlayer.name, card))
                    prompt_user()
                    i = input()
                    if i.lower() == 'y':
                        #Handle Challenge#
                        return challenge(cPlayer, player, card, board)
                    elif i.lower() == 'n':
                        not_answered = False
                        return False
                    else:
                        print("Please put in 'y' for yes or 'n' for no")
    else:
        for (cPlayer,chal,card) in challengers:
            if chal:
                not_answered = True
                while not_answered:
                    print("""Notice for {}:\n{} is counteracting your action by claiming that you do not have a {}.\nWould you like to challenge this? y/n""".format(player.name, cPlayer.name, card))
                    prompt_user()
                    i = input()
                    if i.lower() == 'y':
                        return not(challenge(player, cPlayer, card, board))
                    elif i.lower() == 'n':
                        not_answered = False
                        return False
                    else:
                        print("Please put in 'y' for yes or 'n' for no")
    return True


def challenge(player: Player, challenger: Player, claimedCard: CardType, board: Board):
    """
    Resolve Challenge - handle challenge upkeep,
    
    Return True if action should still be carried out, False if the action does not happen
    """
    has_card = False
    c_idx = None
    for idx, card in enumerate(player.hand):
        if card.type == claimedCard:
            c_idx = idx
            has_card = True
    

    if has_card:
        print("{} had a {}".format(player.name, claimedCard))
        card = player.hand.pop(c_idx)
        board.deck.add_bottom(card)
        player.hand.append(board.deck.draw_cards(1)[0])
        liar = challenger
    else: 
        print("{} did not have a {}".format(player.name, claimedCard))
        liar = player

    r_idx = random.randint(0, len(liar.hand)-1)

    revealed_card = liar.hand.pop(r_idx)
    liar.influence -= 1
    print("{} has been revealed".format(revealed_card.type))
    board.revealed.append(revealed_card)
    if liar.influence == 0:
        board.lost_influence.append(liar)
        print("{} has lost influence".format(liar.name))
    return liar == player

def targetting_players(possible_targets:List[Player], player:Player):
    s = """Notice for {}:\n Return in numeric value which player you would like to target.\n""".format(player.name)
    for idx, i in enumerate(possible_targets):
        s += "{} : {} \n".format(idx, i.name)
    print(s)
    not_answered = True
    while not_answered:
        prompt_user()
        i = input()
        if not i.isnumeric():
            print("Please put in a numeric value")
        elif int(i) >= 0 and int(i) <= len(possible_targets):
            return possible_targets[int(i)]
        else:
            print("Please put in a value between 0 and {}".format(len(possible_targets)))


def get_possible_challengers(board: Board, player: Player):
    possible_challengers = board.players.copy()
    possible_challengers.remove(player)
    for i in board.lost_influence:
        possible_challengers.remove(i)
    return possible_challengers

def process_action(action: int, player: Player, board : Board):
    if action == 0:
        #Income#
        player.bank += 1
        board.end_turn()
    if action == 1:
        action = "take Foreign Aid"
        possible_challengers = get_possible_challengers(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.CounterActions.BlockForeignAid.value, board)
        if allowed:
            player.bank += 2
        board.end_turn()
    elif action == 2 and player.bank >= 7:
        #coup#
        possible_challengers = get_possible_challengers(board, player)
        targetted_user = targetting_players(possible_challengers, player)
        player.bank -= 7
        r_idx = random.randint(0, len(targetted_user.hand)-1)
        revealed_card = targetted_user.hand.pop(r_idx)
        targetted_user.influence -= 1
        print("{} has been revealed".format(revealed_card.type))
        board.revealed.append(revealed_card)
        if targetted_user.influence == 0:
            board.lost_influence.append(targetted_user)
            print("{} has lost influence".format(targetted_user.name))
        board.end_turn()
    elif action == 3:
        action = "Tax"
        possible_challengers = get_possible_challengers(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.ActionPowers.Tax.value, board, True)
        if allowed:
            player.bank += 3
        board.end_turn()

    elif action == 4:
        action = "Assassinate"
        possible_challengers = get_possible_challengers(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.ActionPowers.Assassinate.value, board, True)
        if (allowed and player.bank >= 3):
            player.bank -= 3
            possible_targets = get_possible_challengers(board, player)
            targetted_user = targetting_players(possible_targets, player)
            
            assassin_allowed = counter_action(player, [targetted_user], action, constants.CounterActions.BlockAssassination.value, board)
            if assassin_allowed:
                if len(targetted_user.hand) >0:
                    r_idx = random.randint(0, len(targetted_user.hand)-1)
                    revealed_card = targetted_user.hand.pop(r_idx)
                    targetted_user.influence -= 1
                    print("{} has been revealed".format(revealed_card.type))
                board.revealed.append(revealed_card)
                if targetted_user.influence == 0:
                    if not (targetted_user in board.lost_influence):
                        board.lost_influence.append(targetted_user)
                        print("{} has lost influence".format(targetted_user.name))
        board.end_turn()

    elif action == 5:
        action = "Steal"
        possible_challengers = get_possible_challengers(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.ActionPowers.Steal.value, board, True)
        if allowed:
            possible_targets = get_possible_challengers(board, player)
            targetted_user = targetting_players(possible_targets, player)
            if targetted_user in board.players:
                steal_allowed = counter_action(player, [targetted_user], action, constants.CounterActions.BlockStealing.value, board)
                if steal_allowed:
                    targetted_user.bank -= 2
                    player.bank += 2
                    print("{} now has {} coins in bank".format(targetted_user.name, targetted_user.bank))
        board.end_turn()
    elif action == 6:
        action = "Exchange"
        possible_challengers = get_possible_challengers(board, player)
        allowed = counter_action(player, possible_challengers, action , constants.ActionPowers.Exchange.value, board, True)

        if allowed:
            # Force player to select from cards in their hand and two random cards drawn from the deck.
            new_cards = board.deck.draw_cards(constants.NUM_EXCHANGE)
            possible_cards = player.hand + new_cards # type: List[Card]

            # Display cards
            for card_index in range(len(possible_cards)):
                print(str(card_index) + ": " + str(possible_cards[card_index].type))
            print("Please select {} card(s) by typing numbers spaced apart into the prompt. "
                  "If a valid input is not provided then you will keep your current cards".format(player.influence))

            prompt_user()
            index_selected = input()

            # Determine cards selected
            parsed_cards = index_selected.split(" ")
            parsed_cards = [int(i) for i in parsed_cards]

            selected_cards = []
            for i in range(player.influence):
                selected_cards.append(possible_cards[parsed_cards[i]])

            # Handle exchange transaction
            if len(selected_cards) == player.influence:
                player.hand = selected_cards

                # Add unselected cards back to the deck
                for j in range(len(possible_cards)):
                    if j not in parsed_cards:
                        deck.add_bottom(possible_cards[j])
            else:
                for card in possible_cards[player.influence:]:
                    deck.add_bottom(card)
            board.end_turn()


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
        for _ in range(constants.NUM_COPIES):
            d.append(Card(t))

    deck = Deck(d)
    board = Board(player_list, deck)
    repl(board)

