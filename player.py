from card import Card
from typing import List
#Set up a super simply 
class Player():
    def display_hand(self):
        print("{} has the following cards:".format(self.name))
        for i in range(len(self.hand)):
            card = self.hand[i]
            print("{} - Type: {}".format(i, card.type))
    
    def display_hand(self):
        print("{} has in their bank:".format(self.name))
        print("{}").format(self.bank)
        
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.bank = 2 # initial monies
        self.influence = 2