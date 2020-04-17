import sys
import constants
import random

from deck import Deck
from player import Player, RandomPlayer
from board import Board
from deck import Deck
from card import Card, CardType
from typing import List, Tuple
from utils import check_win, get_alive_opponents, prompt_user, process_counter, lose_card
from constants import RecordedActions


def process_input(input_string: str, player: Player, board: Board):
    input_string.strip()
    input_list = input_string.split()

    if input_list[0] == "help":
        print(constants.HELP_STRING)
    elif input_list[0] == "play":
        selected_action = player.select_action()
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
            if isinstance(p_turn, RandomPlayer):
                p_turn.select_action()
            else:
                print("{} it is your turn".format(p_turn.name))
                prompt_user()
                i = input()
                process_input(i, p_turn, board)
            # End of action
            game_over, winner = check_win(board.players)

    print("{} has won the game!".format(winner))


def counter_action(player: Player, cPlayers: List[Player], action: str, counterCards: List[CardType], board: Board,
                   against_claim: bool = False):
    """
    Return True if action should still be carried out, False if the action does not happen
    """
    # Format string to ask players#
    challengers = []
    s = "{} is trying to {}, would you like to counteract this action?\n Please type one of the following choices:\n 0 - Do nothing\n".format(
        player.name, action)
    for idx, card in enumerate(counterCards):
        if not against_claim:
            s += " {} - Counter - Claim to have {}\n".format(idx + 1, card)
        else:
            s += " {} - Counter - Deny {} claim to having a {}\n".format(idx + 1, player.name + "\'s", card)

            # Loop through possible players and see if they would like to invoke a counteraction#
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
                    challengers.append((p, False, None))
                else:
                    i -= 1
                    challengers.append((p, True, counterCards[i]))
                not_answered = False
            else:
                print("Please put in a value between 0 and {}".format(len(counterCards)))
        constants.clear_terminal()
        print("just past clear")

    # PseudoRandom way of representing people speaking out of turn#
    random.shuffle(challengers)

    # Check if anyone chose to invoke a counter action and determine if the initial player would like to challenge the counteraction#
    if not against_claim:
        for (cPlayer, chal, card) in challengers:
            if chal:
                not_answered = True
                while not_answered:
                    print(
                        """Notice for {}:\n{} is counteracting your action by claiming to have {}.\nWould you like to challenge this? y/n""".format(
                            player.name, cPlayer.name, card))
                    prompt_user()
                    i = input()
                    if i.lower() == 'y':
                        # Handle Challenge#
                        return challenge(cPlayer, player, card, board)
                    elif i.lower() == 'n':
                        not_answered = False
                        return False
                    else:
                        print("Please put in 'y' for yes or 'n' for no")
    else:
        for (cPlayer, chal, card) in challengers:
            if chal:
                not_answered = True
                while not_answered:
                    print(
                        """Notice for {}:\n{} is counteracting your action by claiming that you do not have a {}.\nWould you like to challenge this? y/n""".format(
                            player.name, cPlayer.name, card))
                    prompt_user()
                    i = input()
                    if i.lower() == 'y':
                        return not (challenge(player, cPlayer, card, board))
                    elif i.lower() == 'n':
                        not_answered = False
                        process_counter(cPlayer, card, board)
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

    lose_card(liar, board)

    return liar == player


def process_action(action: int, player: Player, board: Board):
    if action == constants.ActionType.Income:
        # Income#
        player.bank += 1
        board.update_player_actions(player, RecordedActions.Income)
        board.end_turn()

    if action == constants.ActionType.Foreign_aid:
        action = "take Foreign Aid"
        possible_challengers = get_alive_opponents(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.CounterActions.BlockForeignAid.value,
                                 board)
        if allowed:
            player.bank += 2
            for p in board.players:
                if not player:
                    board.update_player_actions(p, RecordedActions.Fail_Block_Foreign)

        board.update_player_actions(player, RecordedActions.Foreign_aid)
        board.end_turn()

    elif action == constants.ActionType.Coup and player.bank >= 7:
        # coup#
        alive_opponents = get_alive_opponents(board, player)
        targeted_user = player.select_targeted_player(constants.ActionType.Coup, alive_opponents)
        player.bank -= 7

        lose_card(targeted_user, board)

        board.update_player_actions(player, RecordedActions.Coup)
        board.end_turn()

    elif action == constants.ActionType.Tax:
        action = "Tax"
        possible_challengers = get_alive_opponents(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.ActionPowers.Tax.value, board, True)
        if allowed:
            player.bank += 3
        board.update_player_actions(player, RecordedActions.Tax)
        board.end_turn()

    elif action == constants.ActionType.Assassinate and player.bank >= 3:
        action = "Assassinate"
        alive_opponents = get_alive_opponents(board, player)
        targeted_user = player.select_targeted_player(constants.ActionType.Assassinate, alive_opponents)

        allowed = counter_action(player, [targeted_user], action, constants.ActionPowers.Assassinate.value, board,
                                 True)

        if allowed and targeted_user.influence > 0:
            player.bank -= 3

            assassin_allowed = counter_action(player, [targeted_user], action,
                                              constants.CounterActions.BlockAssassination.value, board)
            if assassin_allowed:
                board.update_player_actions(targeted_user, RecordedActions.Fail_Block_Assassination)
                if len(targeted_user.hand) > 0:
                    r_idx = random.randint(0, len(targeted_user.hand) - 1)
                    revealed_card = targeted_user.hand.pop(r_idx)
                    targeted_user.influence -= 1
                    print("{} has been revealed".format(revealed_card.type))
                board.revealed.append(revealed_card)
                if targeted_user.influence == 0:
                    if not (targeted_user in board.lost_influence):
                        board.lost_influence.append(targeted_user)
                        print("{} has lost influence".format(targeted_user.name))

        board.update_player_actions(player, RecordedActions.Assassinate)
        board.end_turn()

    elif action == constants.ActionType.Steal:
        action = "Steal"

        alive_opponents = get_alive_opponents(board, player)
        targeted_user = player.select_targeted_player(constants.ActionType.Steal, alive_opponents)

        allowed = counter_action(player, [targeted_user], action, constants.ActionPowers.Steal.value, board, True)

        if allowed:
            if targeted_user in board.players:

                # TODO This is confusing
                steal_allowed = counter_action(player, [targeted_user], action,
                                               constants.CounterActions.BlockStealing.value, board)
                if steal_allowed:
                    board.update_player_actions(targeted_user, RecordedActions.Fail_Block_Steal)

                    # TODO this might not be two coins?
                    targeted_user.bank -= 2
                    player.bank += 2
                    print("{} now has {} coins in bank".format(targeted_user.name, targeted_user.bank))

        board.update_player_actions(player, RecordedActions.Steal)
        board.end_turn()

    elif action == constants.ActionType.Exchange:
        action = "Exchange"
        possible_challengers = get_alive_opponents(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.ActionPowers.Exchange.value, board,
                                 True)

        if allowed:
            # Force player to select from cards in their hand and two random cards drawn from the deck.
            new_cards = board.deck.draw_cards(constants.NUM_EXCHANGE)
            possible_cards = player.hand + new_cards  # type: List[Card]

            selected_cards = player.select_cards(possible_cards, player.influence)

            bottom_cards = []
            # Handle exchange transaction
            if len(selected_cards) == player.influence:
                player.hand = selected_cards

            for card in possible_cards:
                if card not in player.hand:
                    board.deck.add_bottom(card)
                    bottom_cards.append((card, len(board.deck)))

            board.update_deck_knowledge(player, bottom_cards)
            board.update_player_actions(player, RecordedActions.Exchange)
            board.end_turn()
