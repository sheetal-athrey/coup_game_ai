import sys
import constants
import random

from deck import Deck
from player import Player, RandomPlayer, HeuristicPlayer
from board import Board
from deck import Deck
from card import Card, CardType
from typing import List, Tuple, Optional
from utils import check_win, get_alive_opponents, process_counter, lose_card, block_print, enable_print
from constants import RecordedActions, prompt_user, get_action_type_from_counter_decision, get_card_from_counter_decision, SELECT_ACTION_STRING, CounterDecisions


def process_input(input_string: str, player: Player, board: Board):
    input_string.strip()
    input_list = input_string.split()

    if input_list[0] == "help":
        print(constants.HELP_STRING)
    elif input_list[0] == "play":
        print(SELECT_ACTION_STRING)
        selected_action = player.select_action()
        process_action(selected_action, player, board)
    elif input_list[0] == "hand":
        board.display_hand(player)
    elif input_list[0] == "board":
        board.display_board()
    elif input_list[0] == "bank":
        board.display_bank(player)
    else:
        print("Type 'help' for instructions")
    print()


def repl(board: Board) -> Player:
    """
    players - Players list - A list of player objects that represent the players.
    board - Board - a fresh board to start the game
    """
    game_over, winner = check_win(board.players)
    while not game_over:
        p_turn = board.players[board.turn]
        # print("                     Current Turn: ", p_turn.name)
        # print("                     Player's influence ", [p.influence for p in board.players])
        # print("                     Player's bank ", [p.bank for p in board.players])
        # print("                     Player's hand size", [len(p.hand) for p in board.players])

        if p_turn.influence <= 0:
            board.end_turn()
        else:
            #print("THIS IS P_TURN", p_turn.name)
            if isinstance(p_turn, RandomPlayer) or isinstance(p_turn, HeuristicPlayer):
                selected_action = p_turn.select_action()
                enable_print()
                print(p_turn.name, selected_action)
                block_print()
                process_action(selected_action, p_turn, board)
            else:
                print("{} it is your turn".format(p_turn.name))
                prompt_user()
                i = input()

                while not i.isalnum():
                    print("{} it is your turn".format(p_turn.name))
                    prompt_user()
                    i = input()
                process_input(i, p_turn, board)

            # End of action
        game_over, winner = check_win(board.players)
    print("{} has won the game!".format(winner.name))
    return winner
    


def counter_action(player: Player, cPlayers: List[Player], action: constants.ActionType, card_claimed: Optional[constants.CardType],
                   board: Board):
    """
    Return True if action should still be carried out, False if the action does not happen
    """
    decided_counteractors = []
    # Loop through possible players and see if they would like to invoke a counteraction#


    for p in cPlayers:
        counter_decision = p.make_counter_decision(action, player)
        if counter_decision != constants.CounterDecisions.DoNothing:
            decided_counteractors.append((p, counter_decision))

    # PseudoRandom way of representing people speaking out of turn
    random.shuffle(decided_counteractors)

    if len(decided_counteractors) == 0:
        return True

    selected_counteractor = decided_counteractors[0]

    if selected_counteractor[1] == constants.CounterDecisions.Challenge:
        return not (challenge(player, selected_counteractor[0], card_claimed, board))
    else:

        # Update board state about blocking based on ???
        counter_to_recording = {
            CounterDecisions.BlockAssassination : RecordedActions.Block_Assassination,
            CounterDecisions.BlockForeignAid : RecordedActions.Block_Foreign_Aid,
            CounterDecisions.BlockStealingAmbassador : RecordedActions.Block_Steal,
            CounterDecisions.BlockStealingCaptain : RecordedActions.Block_Steal
        }

        counter_counter_decision = player.make_counter_decision(
                                            get_action_type_from_counter_decision(selected_counteractor[1]),
                                            selected_counteractor[0])

        if counter_counter_decision == constants.CounterDecisions.DoNothing:
            board.update_player_actions(selected_counteractor[0], counter_to_recording[selected_counteractor[1]])
            return False
        elif counter_counter_decision == constants.CounterDecisions.Challenge:
            allowed = challenge(selected_counteractor[0], player, get_card_from_counter_decision(selected_counteractor[1]), board)
            if not allowed:
                board.update_player_actions(selected_counteractor[0], counter_to_recording[selected_counteractor[1]])
            return allowed
        else:
            raise Exception("You can't counteract here.")


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


def process_action(action: constants.ActionType, player: Player, board: Board):
    if action == constants.ActionType.Income:
        # Income#
        print("{} takes Income".format(player.name))
        player.bank += 1
        board.update_player_actions(player, RecordedActions.Income)
        board.end_turn()

    if action == constants.ActionType.Foreign_aid:
        print("{} attempts to take ForeignAid".format(player.name))
        possible_challengers = get_alive_opponents(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.CounterActions.BlockForeignAid.value,
                                 board)

        if allowed:
            print("{} takes ForeignAid".format(player.name))
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
        print("{} coups {}".format(player.name, targeted_user.name))
        player.bank -= 7

        lose_card(targeted_user, board)

        board.update_player_actions(player, RecordedActions.Coup)
        board.end_turn()

    elif action == constants.ActionType.Tax:
        print("{} attempts to take Tax".format(player.name))
        possible_challengers = get_alive_opponents(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.ActionPowers.Tax.value, board)
        if allowed:
            print("{} takes Tax".format(player.name))
            player.bank += 3
        board.update_player_actions(player, RecordedActions.Tax)
        board.end_turn()

    elif action == constants.ActionType.Assassinate and player.bank >= 3:
        alive_opponents = get_alive_opponents(board, player)
        targeted_user = player.select_targeted_player(constants.ActionType.Assassinate, alive_opponents)

        allowed = counter_action(player, [targeted_user], action, constants.ActionPowers.Assassinate.value, board)

        print("{} attempts to Assassinate {}".format(player.name, targeted_user.name))

        if allowed and targeted_user.influence > 0:
            print("{} Assassinates {}".format(player.name, targeted_user.name))
            player.bank -= 3
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

        alive_opponents = get_alive_opponents(board, player)
        targeted_user = player.select_targeted_player(constants.ActionType.Steal, alive_opponents)
        allowed = counter_action(player, [targeted_user], action, constants.ActionPowers.Steal.value, board)

        if allowed:
            board.update_player_actions(targeted_user, RecordedActions.Fail_Block_Steal)
            print("{} Steals from {}".format(player.name, targeted_user.name))
            # TODO this might not be two coins?
            steal_amt = min(2, targeted_user.bank)
            player.bank += steal_amt
            targeted_user.bank -= steal_amt
            print("------------------------------------{} now has {} coins in bank".format(targeted_user.name, targeted_user.bank))
        else:
            print("------------------the steal was blocked")
        board.update_player_actions(player, RecordedActions.Steal)
        board.end_turn()

    elif action == constants.ActionType.Exchange:
        print("{} attempts to exchange with the court deck".format(player.name))

        possible_challengers = get_alive_opponents(board, player)
        allowed = counter_action(player, possible_challengers, action, constants.ActionPowers.Exchange.value, board)

        if allowed:
            print("{} exchange {} cards with the court deck".format(player.name, len(player.hand)))
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
                    bottom_cards.append((card, board.deck.size()))

            board.update_deck_knowledge(player, bottom_cards)
        board.update_player_actions(player, RecordedActions.Exchange)
        board.end_turn()
