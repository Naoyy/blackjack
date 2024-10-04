#fonctions pour créer une main de blackjack 

from random import shuffle
from config import End

def get_cards(deck:list,pos:int,start=True)->tuple[list,list,int]:
    """returns cards (hand), deck (full deck) and position"""
    increment = 1
    if start: # get start cards
        increment = 4
    if pos + increment > 52:
        cards = deck[pos:] 
        shuffle(deck)
        return cards + deck[:(pos+increment)%52],deck, (pos+increment)%52
    return deck[pos:pos+increment],deck,pos+increment

def get_values(hand:list)->list: 
    """
    hand = list of Cards (object)
    """
    return [card.value for card in hand]

def get_score(hand:list)-> int:
    """
    hand: list of cards (object), we shall calculate the score of this hand
    """
    val = get_values(hand)
    val.sort()
    if 1 in val: #As = 1 ou 11
        somme=sum(val[val.count(1):])
        for i in range (val.count(1)):
            if somme + 11 > 21:
                somme+=1
            else:
                somme+= 11
        return somme
    return sum(val)

def player_decision(player_hand)->str:
    if len(player_hand)>2:
        choice = input("what do you want to do ? (hit/stay)").lower()
    elif (player_hand[0].value == player_hand[1].value):
        choice = input("what do you want to do ? (double/split/hit/stay)").lower()
    else: 
        choice = input("what do you want to do ? (double/hit/stay)").lower()
    return choice

def pick (deck:list,pos:int,hand:list)->tuple[list,int,list]: 
    """return deck, pos, new hand of cards"""
    tmp,deck,pos = get_cards(deck,pos,start=False)
    
    hand += (tmp[0],)
    return deck, pos, hand


def hit(deck:list,pos:int,player_hand:list,house_hand:list)->tuple[int,list,int,list,list]:
    choice = ""
    while (get_score(player_hand)<21) and (choice != "stay"):
        deck, pos, player_hand = pick(deck,pos,player_hand)

        if get_score(player_hand)>21:
                print("LOSS\nPlayer Bust\n")
                print(f"House: \n\n {[card.full_name for card in house_hand]} ({get_score(house_hand)}) \n\n Player: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
                return End.lose,deck,pos, player_hand, house_hand
        
        print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} \n\n Player: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
        choice = player_decision(player_hand)      

    return End.proceed,deck,pos,player_hand,house_hand

def double (deck:list,pos:int,player_hand:list,house_hand:list)->tuple[int,list,int,list,list]:
    deck, pos, player_hand = pick(deck,pos,player_hand)
    print(f"House: \n\n {house_hand[0].full_name} \n\n Player: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
    
    if get_score(player_hand)>21:
        print("LOSS\nPlayer Bust\n")
        return End.lose,deck,pos,player_hand,house_hand
    
    return End.proceed,deck,pos,player_hand,house_hand

# def split(deck:list,pos:int,player_hand:list,house_hand:list)->tuple[int,list,int,list,list]:
#     split_counter = 1
#     player_hand_1 = player_hand.copy()[0]
#     player_hand_2 = player_hand.copy()[1]

#     deck,pos,player_hand_1 = pick(deck,pos,player_hand_1)

#     choice_1 = player_decision(player_hand_1)
#     if choice_1 == "hit": 
#         while get_score(player_hand_1)<21 or choice != "stay":
#             tmp,deck,pos= get_cards(deck,pos,start=False)
#             player_hand_1 += tmp
#             if get_score(player_hand_1)>21:
#                     print("bust")
#                     return End.lose,deck,pos
#             print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} \n\n Player: {[card.full_name for card in player_hand_1]} ({get_score(player_hand_1)})")
#             choice = player_decision(player_hand_1)

def split(deck,pos,player_hand:list)->tuple[list,int,list,list]:
    player_hand_1 = player_hand[0]
    player_hand_2 = player_hand[1]

    deck,pos,player_hand_1 = pick(deck,pos,player_hand_1)
    deck,pos,player_hand_2 = pick(deck,pos,player_hand_2)

    return deck,pos,player_hand_1,player_hand_2