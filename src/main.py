from utils.turn import deck_shuffle
from helpers.deck_build import Card
from config import Color, Value


couleurs = [Color.pique,Color.coeur,Color.trefle,Color.carreau]

# créer un deck
nsdeck = [Card(val,col) for val in range(1,14) for col in couleurs] #non shuffled deck 
sdeck = deck_shuffle(nsdeck) #shuffled deck

def start_game():
    pass


if __name__ == "__main__":
    start_game()