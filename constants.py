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

NUM_COPIES = 3
NUM_EXCHANGE = 2
STARTING_MONEY = 2
STARTING_INFLUENCE = 2


def clear_terminal():
    os.system('cls||clear')


class CardType(Enum):
    Ambassador = "Ambassador"
    Assassin = "Assassin"
    Contessa = "Contessa"
    Captain = "Captain"
    Duke = "Duke"


class ActionType(Enum):
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


class CounterActions(Enum):
    BlockForeignAid = [CardType.Duke]
    BlockAssassination = [CardType.Contessa]
    BlockStealing = [CardType.Captain, CardType.Ambassador]


class ActionPowers(Enum):
    Tax = [CardType.Duke]
    Assassinate = [CardType.Assassin]
    Steal = [CardType.Captain]
    Exchange = [CardType.Ambassador]