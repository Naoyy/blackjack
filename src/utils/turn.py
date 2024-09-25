#fonctions pour créer une main de blackjack 

from random import sample

def deck_shuffle(deck:list) -> list:
    return sample(deck,k=len(deck))