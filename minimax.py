from typing import List, Tuple, Optional
from constants import RecordedActions, ActionType, CounterDecisions
from player import PlayerView, HeuristicPlayer
from RandomPlayout import randomPlayout
import numpy as np
import sys
import random


def get_alive_opponent_ids(influence_list: List[int], current_player: int) -> List[int]:

    alive_opponents = []

    for player_id in range(len(influence_list)):
        if influence_list[player_id] > 0 and player_id != current_player:
            alive_opponents.append(player_id)

    return alive_opponents


def generate_possible_actions(p_id: int, influence_list: List[int], bank_list: List[int], p_view:PlayerView
) -> List[Tuple[ActionType,Optional[int]]]:

    if bank_list[p_id] >= 10:
        return [(ActionType.Coup, i) for i in range(len(influence_list)) if (influence_list[i] > 0 and p_id != i)]

    player_p = p_view.players[p_id]
    claimed_c = p_view.mod_claimed_cards([player_p])[0]
    action_list = []

    for action in ActionType:
        if action.value[0] < 7:  # one of the 7 original actions
            if action == ActionType.Income or action == ActionType.Foreign_aid or (action == ActionType.Tax and claimed_c[4]>(random.random()/2)) or (action == ActionType.Exchange and claimed_c[0]>(random.random()/2)):

                action_list.append((action, None))
            else:
                if (action == ActionType.Assassinate and bank_list[p_id] >= 3 and (claimed_c[1]>random.random()/2)) or \
                        (action == ActionType.Steal and (claimed_c[3]> random.random()/2)) or \
                        (action == ActionType.Coup and bank_list[p_id] >= 7):

                    for player_id in range(len(influence_list)):
                        if influence_list[player_id] > 0 and player_id != p_id:
                            action_list.append((action, player_id))
    return action_list


def eval(influence: List[int], bank: List[int], p_view: PlayerView) -> List[int]:
    # high is good.
    out = []
    inf_value = 100
    money_value = 10

    for i in range(len(influence)):
        inf = influence[i]
        money = bank[i]
        score = 0
        if inf >= 1:
            #Add scores
            score += inf * inf_value
            score += money * money_value
        out.append(score)

    #normalize score to be 100
    out = np.array(out)
    out = out * (100.0 / np.sum(out))
    return out


########################################################################################################################
# Any place that requires multiple calls to get a single score value should just use the expected probability as weights for the child scores
########################################################################################################################

class MinimaxPlayer(HeuristicPlayer):
    def __init__(self, name: str, depth: int = 2, random_playout: bool = False):
        super().__init__(name)
        self.targetDepth = depth
        self.random_playout = random_playout
        self.id = "Minimax" + str(self.targetDepth)
        if self.random_playout:
            self.id = "Playout" + str(self.targetDepth)
        self.target = None

    def select_action(self) -> ActionType:
        influence = []
        bank = []
        for pi in self.player_view.players:
            influence.append(pi.influence)
            bank.append(pi.bank)
        ((action,target),_) = self.minimax_action(0, self.targetDepth, self.player_view.players.index(self), influence, bank, self.player_view)
        self.target = target
        return action

    def make_counter_decision(self, action_taken: ActionType, acting_player: 'Player') -> CounterDecisions:
        influence = []
        bank = []
        for pi in self.player_view.players:
            influence.append(pi.influence)
            bank.append(pi.bank)
        (counter, _) = self.minimax_counter_decisions(0, self.targetDepth, action_taken, self.player_view.players.index(acting_player),
                              [self.player_view.players.index(self)], influence, bank, self.player_view)

        print("COUNTER------------------------------------------------  ", counter)
        return counter[0]

    def select_targeted_player(self, action_taken: ActionType, possible_targets: List['Player']) -> 'Player':
        return self.player_view.players[self.target]

    def minimax_action(self,currDepth: int, targetDepth: int, p_id: int, influence: List[int], bank: List[int], p_view: PlayerView) \
            -> ((Optional[ActionType], Optional[int]), List[float]):

        num_players = len(bank)

        if influence[p_id] < 1:
            return self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)

        influence_array = np.array(influence)
        if currDepth == targetDepth or (influence_array > 0).sum() == 1:
            if self.random_playout:
                return (None,None), randomPlayout(influence, bank, p_id, 5, p_view)
            else:
                return (None, None), eval(influence, bank, p_view)


        # Increment depth check
        currDepth += 1
        possible_actions = generate_possible_actions(p_id, influence, bank, p_view)

        action_scores = []
        alive_opponents = get_alive_opponent_ids(influence, p_id)

        for action, target in possible_actions:

            if action == ActionType.Income:

                # Update player view with Income Taken
                ra = RecordedActions.Income
                p_view.update_action(p_id, ra, 1)
                bank[p_id] += 1

                _, score = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)

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
                _, score = self.minimax_counter_decisions(currDepth, targetDepth, action, p_id, alive_opponents, influence, bank, p_view)

                # Revert action
                p_view.update_action(p_id, ra, -1)

                action_scores.append(score)

            elif action == ActionType.Coup:

                ra = RecordedActions.Coup

                p_view.update_action(p_id, ra, 1)
                influence[target] -= 1
                bank[p_id] -= 7

                _, score = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                bank[p_id] += 7
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

                _, score = self.minimax_counter_decisions(currDepth, targetDepth, action, p_id, [target], influence, bank, p_view)

                p_view.update_action(p_id, ra, -1)
                action_scores.append(score)

        my_scores = list(map(lambda l : l[p_id], action_scores))
        my_scores = np.array(my_scores)
        max_idx = np.argmax(my_scores)

        return possible_actions[max_idx], action_scores[max_idx]


    def minimax_counter_decisions(self,currDepth: int, targetDepth: int, action: ActionType, actor_id: int,
                                  possible_counteractor_ids: List[int], influence: List[int], bank: List[int],
                                  p_view: PlayerView) -> ((CounterDecisions, int), List[float]):

        #handles the case in which the player is calling this while being countered, mostly due to how we recieve inputs from
        #baord. Thus not an issue besides when directly invoked from player
        if action == ActionType.Block_Assassination:
            return self.minimax_block_action(currDepth, targetDepth, ActionType.Assassinate, possible_counteractor_ids[0], CounterDecisions.BlockAssassination, actor_id, influence, bank, p_view)
        elif action == ActionType.Block_Foreign_Aid:
            return self.minimax_block_action(currDepth, targetDepth, ActionType.Foreign_aid, possible_counteractor_ids[0], CounterDecisions.BlockForeignAid, actor_id, influence, bank, p_view)
        elif action == ActionType.Block_Steal_Ambassador:
            return self.minimax_block_action(currDepth, targetDepth, ActionType.Steal, possible_counteractor_ids[0], CounterDecisions.BlockStealingAmbassador, actor_id, influence, bank, p_view)
        elif action == ActionType.Block_Steal_Captain:
            return self.minimax_block_action(currDepth, targetDepth, ActionType.Steal, possible_counteractor_ids[0], CounterDecisions.BlockStealingCaptain, actor_id, influence, bank, p_view)

        num_players = len(influence)
        possible_counters = action.value[1]

        possible_counter_actions = [(CounterDecisions.DoNothing, None if len(possible_counteractor_ids)>1 else possible_counteractor_ids[0])]

        for counter in possible_counters:
            if counter != CounterDecisions.DoNothing:
                for counter_actor in possible_counteractor_ids:
                    possible_counter_actions.append((counter, counter_actor))

        counter_scores = [0.] * len(possible_counter_actions)
        for i in range(len(possible_counter_actions)):
            counter, counter_actor = possible_counter_actions[i]

            if action == ActionType.Foreign_aid or action == ActionType.Block_Foreign_Aid:
                if counter == CounterDecisions.DoNothing:
                    ra = RecordedActions.Fail_Block_Foreign
                    for counter_actor_id in possible_counteractor_ids:
                        p_view.update_action(counter_actor_id, ra, 1)
                    bank[actor_id] += 2
                    _, score = self.minimax_action(currDepth, targetDepth, (actor_id+1)%num_players, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score
                    bank[actor_id] -= 2
                    for counter_actor_id in possible_counteractor_ids:
                        p_view.update_action(counter_actor_id, ra, -1)

                elif counter == CounterDecisions.BlockForeignAid:

                    ra = RecordedActions.Block_Foreign_Aid
                    p_view.update_action(counter_actor, ra, 1)
                    _, score = self.minimax_block_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score
                    p_view.update_action(counter_actor, ra, -1)

            elif action == ActionType.Tax:
                if counter == CounterDecisions.DoNothing:
                    bank[actor_id] += 3
                    _, score = self.minimax_action(currDepth, targetDepth, (actor_id+1)%num_players, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score
                    bank[actor_id] -= 3

                    #challenge when the counteractor does not believe actor == duke
                elif counter == CounterDecisions.Challenge:
                    _, score = self.minimax_chal_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score

            elif action == ActionType.Exchange:
                if counter == CounterDecisions.DoNothing:
                    _,score = self.minimax_action(currDepth, targetDepth, (actor_id+1)%num_players, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score

                    #challenge when the counteractor does not believe actor == ambassador
                elif counter == CounterDecisions.Challenge:
                    _, score = self.minimax_chal_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score

            elif action == ActionType.Steal or action == ActionType.Block_Steal_Captain or action == ActionType.Block_Steal_Ambassador:
                if counter == CounterDecisions.DoNothing:
                    ra = RecordedActions.Fail_Block_Steal
                    p_view.update_action(counter_actor, ra, 1)
                    stolen_val = min(bank[actor_id], bank[counter_actor])
                    bank[actor_id] += stolen_val
                    bank[counter_actor] -= stolen_val
                    _, score = self.minimax_action(currDepth, targetDepth, (actor_id+1)%num_players, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score
                    bank[counter_actor] += stolen_val
                    bank[actor_id] -= stolen_val
                    p_view.update_action(counter_actor, ra, -1)

                    #challenge is when the counteractor does not believe actor == captain
                elif counter == CounterDecisions.Challenge:
                    _, score = self.minimax_chal_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score

                else:# when counteractor says they block the steal
                    ra = RecordedActions.Block_Steal
                    p_view.update_action(counter_actor, ra, 1)
                    _, score = self.minimax_block_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score
                    p_view.update_action(counter_actor, ra, -1)


            elif action == ActionType.Assassinate or action == ActionType.Block_Assassination:
                if counter == CounterDecisions.DoNothing:
                    ra = RecordedActions.Fail_Block_Assassination
                    p_view.update_action(counter_actor, ra, 1)
                    bank[actor_id] -= 3
                    influence[counter_actor] -= 1
                    _, score = self.minimax_action(currDepth, targetDepth, (actor_id+1)%num_players, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score
                    influence[counter_actor] += 1
                    bank[actor_id] += 3
                    p_view.update_action(counter_actor, ra, -1)

                    #challenge is when the counteractor does not believe actor == assassin
                elif counter == CounterDecisions.Challenge:
                    _, score = self.minimax_chal_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score

                else:# when counteractor says they block the assassination
                    ra = RecordedActions.Block_Assassination
                    p_view.update_action(counter_actor, ra, 1)
                    _, score = self.minimax_block_action(currDepth, targetDepth, action, actor_id, counter, counter_actor, influence, bank, p_view)
                    #counter_scores.append(score)
                    counter_scores[i] = score
                    p_view.update_action(counter_actor, ra, -1)
            else:
                raise Exception("{} cannot be countered".format(action))

        diff_scores = [0]
        do_nothing_score = counter_scores[0]
        for i in range(1, len(possible_counter_actions)):
            action,idx = possible_counter_actions[i]
            diff_scores.append(counter_scores[i][idx]-do_nothing_score[idx])
        diff_scores_array = np.array(diff_scores)
        max_diff = np.argmax(diff_scores_array)

        # return possible_counters[max_diff], counter_scores[max_diff]
        return possible_counter_actions[max_diff], counter_scores[max_diff]


    def minimax_block_action(self,currDepth: int, targetDepth: int, action: ActionType, p_id:int, cAction: CounterDecisions, counter_actor_id: int, \
            influence: List[int], bank: List[int], p_view: PlayerView) -> ((CounterDecisions, int), List[float]):
        #Should always call down to miniMaxAction
        num_players = len(influence)
        counter_scores = []
        possible_counters = [CounterDecisions.DoNothing, CounterDecisions.Challenge]
        counter_actor_player = p_view.players[counter_actor_id]
        ca_claimed = p_view.mod_claimed_cards([counter_actor_player])[0]

        for counter in possible_counters:
            if counter == CounterDecisions.DoNothing:
                 _,score = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                 counter_scores.append(score)
            elif action == ActionType.Foreign_aid or action == ActionType.Block_Foreign_Aid:
                prob_duke = (ca_claimed[4]+1)/(sum(ca_claimed)+5)

                # checking the score in case of a success => when counteractor is not duke
                bank[p_id] += 2
                influence[counter_actor_id] -= 1
                _,successscore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                influence[counter_actor_id] += 1
                bank[p_id] -= 2

                # checking the score in case of a failure => when counteractor is a duke
                influence[p_id] -= 1
                _,failurescore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                influence[p_id] += 1

                # weighted sum of success and failure cases = score
                score = (1-prob_duke)*successscore + (prob_duke*failurescore)
                counter_scores.append(score)

            elif action == ActionType.Steal or action == ActionType.Block_Steal_Captain or action == ActionType.Block_Steal_Ambassador:
                prob_captain = (ca_claimed[3]+1)/(sum(ca_claimed)+5)
                prob_ambassador = (ca_claimed[0]+1)/(sum(ca_claimed)+5)
                tot_prob = prob_ambassador + prob_captain

                # checking the score in case of a success => when counteractor is not captain or ambassador
                stolen_val = min(2, bank[counter_actor_id])
                bank[p_id] += stolen_val
                bank[counter_actor_id] -= stolen_val
                influence[counter_actor_id] -= 1
                _,successscore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                influence[counter_actor_id] += 1
                bank[counter_actor_id] += stolen_val
                bank[p_id] -= stolen_val

                # checking the score in case of a failure => when counteractor is captain or ambassador
                influence[p_id] -= 1
                _,failurescore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                influence[p_id] += 1

                # weighted sum of success and failure cases = score
                score = (1-tot_prob)*successscore + (tot_prob*failurescore)
                counter_scores.append(score)

            elif action == ActionType.Assassinate or action == ActionType.Block_Assassination:
                prob_contessa = (ca_claimed[2]+1)/(sum(ca_claimed)+5)

                # checking the score in case of a success => when counteractor is not contessa
                bank[p_id] -= 3
                original_influence = influence[counter_actor_id]
                influence[counter_actor_id] = 0
                _,successscore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                influence[counter_actor_id] = original_influence
                bank[p_id] += 3

                # checking the score in case of a failure => when counteractor is a contessa
                influence[p_id] -= 1
                _,failurescore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
                influence[p_id] += 1

                # weighted sum of success and failure cases = score
                score = (1-prob_contessa)*successscore + (prob_contessa*failurescore)
                counter_scores.append(score)

            else:
                raise Exception("{} cannot be countered".format(action))

        my_scores = list(map(lambda l : l[p_id], counter_scores))
        my_scores = np.array(my_scores)
        max_idx = np.argmax(my_scores)
        return ((possible_counters[max_idx], -100), counter_scores[max_idx])

    def minimax_chal_action(self,currDepth: int, targetDepth: int, action: ActionType, p_id:int, cAction: CounterDecisions, counter_actor_id: int, \
            influence: List[int], bank: List[int], p_view: PlayerView) -> (CounterDecisions, List[float]):

        num_players = len(influence)
        actor_player = p_view.players[p_id]
        ca_claimed = p_view.mod_claimed_cards([actor_player])[0]

        if action == ActionType.Tax:
            top = (ca_claimed[4]+1)
            bottom = (sum(ca_claimed)+5)
            prob_duke = top/bottom

            # checking the score in case of a success => when actor is a duke
            bank[p_id] += 3
            influence[counter_actor_id] -= 1
            _,successscore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[counter_actor_id] += 1
            bank[p_id] -= 3

            # checking the score in case of a failure => when actor is not a duke
            influence[p_id] -= 1
            _,failurescore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[p_id] += 1

            # weighted sum of success and failure cases = score
            score = (prob_duke)*successscore + (1-prob_duke*failurescore)
            return (None, score)

        elif action == ActionType.Exchange:
            prob_ambassador = (ca_claimed[0]+1)/(sum(ca_claimed)+5)

            # checking the score in case of a success => when actor is a ambassador
            influence[counter_actor_id] -= 1
            _,successscore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[counter_actor_id] += 1

            # checking the score in case of a failure => when actor is not a duke
            influence[p_id] -= 1
            _,failurescore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[p_id] += 1

            # weighted sum of success and failure cases = score
            score = (prob_ambassador)*successscore + (1-prob_ambassador*failurescore)
            return (None, score)

        elif action == ActionType.Assassinate or action == ActionType.Block_Assassination:
            prob_assassin = (ca_claimed[1]+1)/(sum(ca_claimed)+5)

            # checking the score in case of a success => when actor is an assassin
            original_influence = influence[counter_actor_id]
            bank[p_id] -= 3
            influence[counter_actor_id] = 0
            _,successscore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[counter_actor_id] = original_influence
            bank[p_id] += 3

            # checking the score in case of a failure => when actor is not an assassin
            influence[p_id] -= 1
            _,failurescore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[p_id] += 1

            # weighted sum of success and failure cases = score
            score = (prob_assassin)*successscore + (1-prob_assassin*failurescore)
            return (None, score)

        elif action == ActionType.Steal or action == ActionType.Block_Steal_Captain or action == ActionType.Block_Steal_Ambassador:
            prob_captain = (ca_claimed[3]+1)/(sum(ca_claimed)+5)

            # checking the score in case of a success => when actor is a captain
            stolen_val = min(2, bank[counter_actor_id])
            bank[p_id] += stolen_val
            bank[counter_actor_id] -= stolen_val
            influence[counter_actor_id] -=1
            _,successscore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[counter_actor_id] += 1
            bank[counter_actor_id] += stolen_val
            bank[p_id] -= stolen_val

            # checking the score in case of a failure => when actor is not a captain
            influence[p_id] -= 1
            _,failurescore = self.minimax_action(currDepth, targetDepth, (p_id+1)%num_players, influence, bank, p_view)
            influence[p_id] += 1

            # weighted sum of success and failure cases = score
            score = (prob_captain)*successscore + (1-prob_captain*failurescore)
            return (None, score)

        else:
            raise Exception("{} cannot be countered".format(action))
