from typing import List, Tuple, Optional
from constants import RecordedActions, ActionType, CounterDecisions
from player import PlayerView
import numpy as np

def generatePossibleActions(p_id: int, influence: List[int], bank: List[int]) -> List[(ActionType,int)]:
    target = 1
    #return [(ActionType.Income, None)]
    return [(ActionType.Assassinate, target)]

def eval(influence: List[int], bank: List[int], p_view: PlayerView) -> List[int]:
    #high is good.
    return influence

###############################################################################################################################################
# Any place that requires multiple calls to get a single score value should just use the expected probability as weights for the child scores #
###############################################################################################################################################

def miniMaxAction(currDepth: int, targetDepth: int, p_id: int, influence: List[int], bank: List[int], p_view: PlayerView) -> ((Optional(ActionType),Optional(int)), List[float]):
    #only optional action on leaf -> assumes depth > 1
    #Either calls back to self or miniMaxCAction
    influence = np.array(influence)
    if currDepth == targetDepth or (influence>0).sum() == 1:
        return ((None, None), eval(influence, bank, p_view))

    currDepth += 1
    poss_actions = generatePossibleActions(p_id, influence, bank)
    num_players = len(bank)

    action_scores = []
    for action, target in poss_actions:
        if action == ActionType.Income:

            ra = RecordedActions.Income
            p_view[ra.value] +=1
            bank[p_id] += 1

            _, score = miniMaxAction(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)

            bank[p_id] -=1
            p_view[ra.value] -=1

            action_scores.append(score)
        else:
            #placeholder
            action_scores.append([0]*num_players)
    
    my_scores = list(map(lambda l : l[p_id], action_scores))
    my_scores = np.array(my_scores)
    max_idx = np.argmax(my_scores)

    return (poss_actions[max_idx], action_scores[max_idx])


def miniMaxCAction(currDepth: int, targetDepth: int, action: ActionType, p_id: int, target_id: int, influence: List[int], bank: List[int], p_view: PlayerView) -> (CounterDecisions, List[float]):
    #Always calls down to miniMaxChalAction
    possible_counters = action.value[1]
    #only need to inclue
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


def miniMaxChalCAction(currDepth: int, targetDepth: int, action: ActionType, p_id:int, cAction: CounterDecisions, challenger_id: int, \
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