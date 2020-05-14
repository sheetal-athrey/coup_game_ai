import os
from enum import Enum, auto

HELP_STRING = """
To play the following actions type 'play #' with # being any of the corresponding numbers:
0 -> Income (+1 Coins)
1 -> Foreign Aid (+2 Coins)
2 -> Coup (-7 Coins, Destroy 1 Influence)
3 -> Tax (+3 Coins; Duke Power)
4 -> Assassinate (-3 Coins, Destroy 1 Influence; Assassin Power)
5 -> Steal (+2 Coins, -2 for other player)
6 -> Exchange (+2 Cards, -2 Cards)

Other Commands include:
'hand' - To see the Influence card(s) you have
'board' - To see how much influence each player has and any revealed cards.
'bank' - To see how many coin(s) you have
"""

SELECT_ACTION_STRING = """
Select action type by selecting a # with # being any of the corresponding numbers:
0 -> Income (+1 Coins)
1 -> Foreign Aid (+2 Coins)
2 -> Coup (-7 Coins, Destroy 1 Influence)
3 -> Tax (+3 Coins; Duke Power)
4 -> Assassinate (-3 Coins, Destroy 1 Influence; Assassin Power)
5 -> Steal (+2 Coins, -2 for other player)
6 -> Exchange (+2 Cards, -2 Cards)"""

NUM_COPIES = 3
NUM_EXCHANGE = 2
STARTING_MONEY = 2
STARTING_INFLUENCE = 2


def prompt_user():
    print("> ", end="")


def clear_terminal():
    os.system('cls||clear')


class CounterDecisions(Enum):
    DoNothing = (0, "Do Nothing")
    Challenge = (1, "Challenge")
    BlockForeignAid = (2, "Block Foreign Aid")
    BlockAssassination = (3, "Block Assassination")
    BlockStealingAmbassador = (4, "Block Stealing as an Ambassador")
    BlockStealingCaptain = (5, "Block Stealing as a Captain")



class CardType(Enum):
    Ambassador = "Ambassador"
    Assassin = "Assassin"
    Contessa = "Contessa"
    Captain = "Captain"
    Duke = "Duke"


class ActionType(Enum):
    Income = (0, [])
    Foreign_aid = (1, [CounterDecisions.DoNothing, CounterDecisions.BlockForeignAid])
    Coup = (2, [])
    Tax = (3, [CounterDecisions.DoNothing, CounterDecisions.Challenge])
    Assassinate = (4, [CounterDecisions.DoNothing, CounterDecisions.Challenge, CounterDecisions.BlockAssassination])
    Steal = (5, [CounterDecisions.DoNothing, CounterDecisions.Challenge, CounterDecisions.BlockStealingAmbassador,
                 CounterDecisions.BlockStealingCaptain])
    Exchange = (6, [CounterDecisions.DoNothing, CounterDecisions.Challenge])
    Block_Foreign_Aid = (7, [CounterDecisions.DoNothing, CounterDecisions.Challenge])
    Block_Steal_Ambassador = (8, [CounterDecisions.DoNothing, CounterDecisions.Challenge])
    Block_Steal_Captain = (9, [CounterDecisions.DoNothing, CounterDecisions.Challenge])
    Block_Assassination = (10, [CounterDecisions.DoNothing, CounterDecisions.Challenge])


class RecordedActions(Enum):
    Income = 0
    Foreign_aid = 1
    Coup = 2
    Tax = 3
    Assassinate = 4
    Steal = 5
    Exchange = 6
    Block_Foreign_Aid = 7
    Block_Steal = 8
    Block_Assassination = 9
    Fail_Block_Foreign = 10
    Fail_Block_Steal = 11
    Fail_Block_Assassination = 12


class CounterActions(Enum):
    BlockForeignAid = [CardType.Duke]
    BlockAssassination = [CardType.Contessa]
    BlockStealing = [CardType.Captain, CardType.Ambassador]


class ActionPowers(Enum):
    Tax = CardType.Duke
    Assassinate = CardType.Assassin
    Steal = CardType.Captain
    Exchange = CardType.Ambassador


def get_action_text(action: ActionType) -> str:
    if action == ActionType.Income:
        return "take income"
    elif action == ActionType.Foreign_aid:
        return "take Foreign Aid"
    elif action == ActionType.Coup:
        return "Coup"
    elif action == ActionType.Tax:
        return "take Tax"
    elif action == ActionType.Steal:
        return "Steal"
    elif action == ActionType.Assassinate:
        return "Assassinate"
    elif action == ActionType.Exchange:
        return "Exchange"
    elif action == ActionType.Block_Assassination:
        return "block Assassination"
    elif action == ActionType.Block_Foreign_Aid:
        return "block Foreign Aid"
    elif action == ActionType.Block_Steal_Ambassador:
        return "block Stealing"
    elif action == ActionType.Block_Steal_Captain:
        return "block Stealing"


def get_action_type_from_counter_decision(decision: CounterDecisions) -> ActionType:
    print(decision)
    if CounterDecisions.BlockAssassination == decision:
        return ActionType.Block_Assassination
    elif CounterDecisions.BlockForeignAid == decision:
        return ActionType.Block_Foreign_Aid
    elif CounterDecisions.BlockStealingAmbassador == decision:
        return ActionType.Block_Steal_Ambassador
    elif CounterDecisions.BlockStealingCaptain == decision:
        return ActionType.Block_Steal_Captain
    else:
        raise Exception("Not possible, check your code! Can't map this counter decision to an action.")


def get_card_from_counter_decision(decision: CounterDecisions) -> CardType:
    if CounterDecisions.BlockAssassination == decision:
        return CardType.Contessa
    elif CounterDecisions.BlockForeignAid == decision:
        return CardType.Duke
    elif CounterDecisions.BlockStealingAmbassador == decision:
        return CardType.Ambassador
    elif CounterDecisions.BlockStealingCaptain == decision:
        return CardType.Captain
    else:
        raise Exception("Not possible, check your code! Can't map this counter decision to a card.")
