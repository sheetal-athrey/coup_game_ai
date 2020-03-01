import os

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
"""

NUM_COPIES = 3

def clear_terminal():
    os.system('cls||clear')