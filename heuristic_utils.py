from enum import Enum, auto


# Need to provide a cost for each player. Player that are out of the game should be included for index but made infinite cost.
def cost(player_views):
    pass

# Need to apply an operation to a state. Each state has actions that are associated with it.
def apply(operation: Operation, state: State, next_player_turn: int, curr_player_turn: int):
    pass



# Are these needed?
class Operation(Enum):
    TakeIncome = auto()
    TakeForeignAid = auto()
    TakeTax = auto()
    Coup = auto()
    Assassinate = auto()
    StealMoney = auto()
    ExchangeCards = auto()
    BlockForeignAid = auto()
    SuccessfulChallengeDuke = auto()
    FailedChallengeDuke = auto()
    BlockAssassination = auto()
    SuccessfulChallengeAssassin = auto()
    SuccessfulChallengeContessa = auto()


class State(Enum):
    BaseState = [[StealMoney, Coup, Assassinate],[Income, ForeignAid],[BlockedForeignAid]]
    AssassinatedState = [[],[Do Nothing],[BlockAssassination]]


    BaseState -->



class Node:

    self.children = []
    self.parent = []


