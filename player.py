from card import Card
#Set up a super simply 
class Player():
    def display_hand(self):
        print("{} has the following cards:".format(self.name))
        for i in range(len(self.hand)):
            card = self.hand[i]
            print("{} - Type: {}".format(i, card.type))

    def __init__(self, name: str, cards: List[Card]):
        self.name = name
        self.hand = cards
        self.bank = 2 # initial monies
        self.influence = 2