# classe pour créer un deck de cartes
from config import Color
val_to_name=[ "None","A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

class Card:
    def __init__(self,name,color) -> None:
        self.value = name if name < 11 else 10 
        self.name = val_to_name[name]
        self.color = color
        self.full_name = val_to_name[name] + " " + color

couleurs = [Color.pique,Color.coeur,Color.trefle,Color.carreau]

non_shuffled_deck = [Card(nam,col) for nam in range(1,14) for col in couleurs]
