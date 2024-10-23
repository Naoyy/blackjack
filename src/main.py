import numpy as np
import os
import pandas as pd
from random import shuffle
from operator import itemgetter 

from helpers.game_builder import Turn
from helpers.deck_build import non_shuffled_deck

def menu(): # TODO peut-être mettre dans utils.start
    if not os.path.isdir("data"):
        os.mkdir("data")
        return menu()
    else:
        if not os.path.isfile("data/cache.csv"):
            choice = input("Welcome !\nWhat do you want to do ? (Start Game / Check Rules / Quit)").lower()
            if choice not in ["start game","check rules","quit"]:
                return menu()
        else:
            choice = input("Welcome !\nWhat do you want to do ? (Start Game / Check Stats / Check Rules / Quit)").lower()
            if choice not in ["start game","check stats","check rules","quit"]:
                return menu()
        return choice


def start_game():
    choice = menu()
    if choice == "quit":
        return
    
    if choice == "check rules":
        print("check rules here: \nhttps://bicyclecards.com/how-to-play/blackjack \n")
        return start_game()
    
    if choice == "start game":
        print("OK GAME STARTING !\n")
        results_df = {"end":[],"player hand":[],"house_hand":[]} #TODO Add more to the df
        
        deck = non_shuffled_deck.copy()
        shuffle(deck)
        # deck = itemgetter(*[36,37,38,24,0,1,24,10,15,17,39])(non_shuffled_deck) # [10,10,10,7,star1,1,7,.,.,.]
        pos = 0
        choice = "continue"

        while choice == "continue":
            end,deck,pos,player_hand,house_hand= Turn.house(*Turn.player(*Turn.start(deck,pos)))
            if type(end) != int:
                for i in range (len(end)):
                    results_df["end"].append(end[i])
                    results_df["player hand"].append([card.full_name for card in player_hand[i]])
                    results_df["house_hand"].append([card.full_name for card in house_hand[i]])
            else: 
                results_df["end"].append(end)
                results_df["player hand"].append([card.full_name for card in player_hand])
                results_df["house_hand"].append([card.full_name for card in house_hand])
            
            choice = input("Continue ? Quit ?").lower()

        results_df = pd.DataFrame(results_df)
        
        if not os.path.isfile("data\\cache.csv"): # première fois qu'on joue
            results_df.to_csv("data\\cache.csv")
            return start_game()
        cache_df = pd.concat([pd.read_csv("data\\cache.csv",index_col=0),results_df])

        cache_df.to_csv("data\\cache.csv")
        return start_game()
    
    if choice == "check stats":
        if not os.path.isfile("data/cache.csv"):
            print("NO STATS YET ! COME BACK WHEN YOU HAVE PLAYED AT LEAST ONCE")
            return start_game()
        df = pd.read_csv("data/cache.csv",index_col=0)
        print(f"win rate: {df[df['end']!=-1]['end'].mean()}")
        print(f"player history: \n\n {df.tail()}")
        return start_game()


if __name__ == "__main__":
    start_game()