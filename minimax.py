from typing import List, Tuple, Optional
from constants import RecordedActions, ActionType, CounterDecisions
from player import PlayerView
import numpy as np


def get_alive_opponent_ids(influence_list: List[int], current_player: int) -> List[int]:

    alive_opponents = []

    for player_id in range(len(influence_list)):
        if influence_list[player_id] > 0 and player_id != current_player:
            alive_opponents.append(player_id)

    return alive_opponents


def generate_possible_actions(p_id: int, influence_list: List[int], bank_list: List[int]) -> List[(ActionType,Optional[int])]:

    if bank_list[p_id] >= 10:
        return [(ActionType.Coup, i) for i in range(len(influence_list)) if (influence_list[i] > 0 and p_id != i)]

    action_list = []

    for action in ActionType:
        if action.value[0] < 7:  # one of the 7 original actions
            if action == ActionType.Income or action == ActionType.Foreign_aid or action == ActionType.Tax or action == ActionType.Exchange:
                action_list.append((action, None))
            else:
                if (action == ActionType.Assassinate and bank_list[p_id] >= 3) or \
                        (action == ActionType.Steal) or \
                        (action == ActionType.Coup and bank_list[p_id] >= 7):

                    for player_id in range(len(influence_list)):
                        if influence_list[player_id] > 0 and player_id != p_id:
                            action_list.append((action, player_id))
    return action_list


def eval(influence: List[int], bank: List[int], p_view: PlayerView) -> List[int]:
    # high is good.
    return influence

########################################################################################################################
# Any place that requires multiple calls to get a single score value should just use the expected probability as weights for the child scores
########################################################################################################################

def minimax_action(currDepth: int, targetDepth: int, p_id: int, influence: List[int], bank: List[int], p_view: PlayerView) \
        -> ((Optional[ActionType], Optional[int]), List[float]):

    num_players = len(bank)

    if influence[p_id] < 1:
        return minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)

    influence_array = np.array(influence)
    if currDepth == targetDepth or (influence_array > 0).sum() == 1:
        return (None, None), eval(influence, bank, p_view)

    # Increment depth check
    currDepth += 1
    possible_actions = generate_possible_actions(p_id, influence, bank)

    action_scores = []
    alive_opponents = get_alive_opponent_ids(influence, p_id)

    for action, target in possible_actions:
        if action == ActionType.Income:

            # Update player view with Income Taken
            ra = RecordedActions.Income
            p_view.update_action(p_id, ra, 1)
            bank[p_id] += 1

            _, score = minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)

            # Remove income taken action
            bank[p_id] -= 1
            p_view.update_action(p_id, ra, -1)

            action_scores.append(score)

        elif action == ActionType.Foreign_aid or action == ActionType.Tax or action == ActionType.Exchange:

            # Update player view
            if action == ActionType.Foreign_aid:
                ra = RecordedActions.Foreign_aid
            elif action == ActionType.Tax:
                ra = RecordedActions.Tax
            elif action == ActionType.Exchange:
                ra = RecordedActions.Exchange
            else:
                raise Exception("Something died")

            p_view.update_action(p_id, ra, 1)

            # Different Paths
            _, score = minimax_counter_decisions(currDepth, targetDepth, action, p_id, alive_opponents, influence, bank, p_view)

            # Revert action
            p_view.update_action(p_id, ra, -1)

            action_scores.append(score)

        elif action == ActionType.Coup:

            ra = RecordedActions.Coup

            p_view.update_action(p_id, ra, 1)
            influence[target] -= 1

            _, score = minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)

            influence[target] += 1
            p_view.update_action(p_id, ra, -1)

            action_scores.append(score)

        elif action == ActionType.Assassinate or action == ActionType.Steal:
            
            if action == ActionType.Assassinate:
                ra = RecordedActions.Assassinate
            elif action == ActionType.Steal:
                ra = RecordedActions.Steal
            else:
                raise Exception("Multi something has died.")

            p_view.update_action(p_id, ra, 1)

            _, score = minimax_counter_decisions(currDepth, targetDepth, action, p_id, [target], influence, bank, p_view)

            p_view.update_action(p_id, ra, -1)
            action_scores.append(score)

    my_scores = list(map(lambda l : l[p_id], action_scores))
    my_scores = np.array(my_scores)
    max_idx = np.argmax(my_scores)

    return possible_actions[max_idx], action_scores[max_idx]


def minimax_counter_decisions(currDepth: int, targetDepth: int, action: ActionType, actor_id: int,
                              possible_counteractor_ids: List[int], influence: List[int], bank: List[int],
                              p_view: PlayerView) -> ((CounterDecisions, int), List[float]):

    num_players = len(influence)
    possible_counters = action.value[1]

    possible_counter_actions = [(CounterDecisions.DoNothing, None)]

    for counter in possible_counters:
        if counter != CounterDecisions.DoNothing:
            for counter_actor in possible_counteractor_ids:
                possible_counter_actions.append((counter, counter_actor))

    counter_scores = []

    for counter, counter_actor in possible_counter_actions:
        if action == ActionType.Foreign_aid:
            if counter == CounterDecisions.DoNothing:
                ra = RecordedActions.Fail_Block_Foreign

                bank[actor_id] += 2
                _, score = minimax_action(currDepth, targetDepth, (actor_id+1)%num_players, influence, bank, p_view)
                counter_scores.append(score)
                bank[actor_id] -= 2

            elif counter == CounterDecisions.BlockForeignAid:

                _, score = minimax_chalc_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)

                counter_scores.append(score)



        elif action == ActionType.Steal:
            pass
        elif action == ActionType.Assassinate:
            pass
        else:
            raise Exception("{} cannot be countered".format(action))

    my_scores = list(map(lambda l : l[actor_id], counter_scores))
    my_scores = np.array(my_scores)
    max_idx = np.argmax(my_scores)

    return possible_counters[max_idx], counter_scores[max_idx]


def minimax_chalc_action(currDepth: int, targetDepth: int, action: ActionType, p_id:int, cAction: CounterDecisions, counteractor_id: int, \
        influence: List[int], bank: List[int], p_view: PlayerView) -> (CounterDecisions, List[float]):
    possible_counters = [CounterDecisions.DoNothing, CounterDecisions.Challenge]
    #Should always call down to miniMaxAction
    counter_scores = []
    for counter in possible_counters: 
        if action == ActionType.Foreign_aid:
            pass
        elif action == ActionType.Steal:
            pass
        elif action == ActionType.Assassinate:
            pass
        else:
            raise Exception("{} cannot be countered".format(action))

    my_scores = list(map(lambda l : l[p_id], counter_scores))
    my_scores = np.array(my_scores)
    max_idx = np.argmax(my_scores)

    return (possible_counters[max_idx], counter_scores[max_idx])