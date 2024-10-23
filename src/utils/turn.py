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
    while (get_score(player_hand)<=21) and (choice != "stay"):
        deck, pos, player_hand = pick(deck,pos,player_hand)

        if get_score(player_hand)>21:
                print("LOSS\nPlayer Bust\n")
                print(f"House: \n\n {[card.full_name for card in house_hand]} ({get_score(house_hand)}) \n\n Player: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
                return End.lose,deck,pos, player_hand, house_hand
        
        print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
        choice = player_decision(player_hand)

    return End.proceed,deck,pos,player_hand,house_hand

def double (deck:list,pos:int,player_hand:list,house_hand:list)->tuple[int,list,int,list,list]:
    deck, pos, player_hand = pick(deck,pos,player_hand)
    print(f"House: \n\n {house_hand[0].full_name} \n\n Player: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
    
    if get_score(player_hand)>21:
        print("LOSS\nPlayer Bust\n")
        return End.lose,deck,pos,player_hand,house_hand
    
    return End.proceed,deck,pos,player_hand,house_hand

def split_cards(deck,pos,player_hand:list)->tuple[list,int,list,list]:
    play_hand = list(player_hand)
    player_hand_1 = [play_hand[0]]
    player_hand_2 = [play_hand[1]]

    deck,pos,player_hand_1 = pick(deck,pos,player_hand_1)
    deck,pos,player_hand_2 = pick(deck,pos,player_hand_2)

    return deck,pos,player_hand_1,player_hand_2

def split_house_turn(deck:list,pos:int,house_hand:list=None)->tuple[int,list,int,list,list]:
    """basically it's house turn to draw cards if needed"""
    
    if get_score(house_hand)>16 and get_score(house_hand)<21:
        return deck, pos, house_hand

    deck,pos,house_hand= pick(deck, pos, house_hand)
    
    if get_score(house_hand)>21:
        return deck,pos,house_hand
    
    return split_house_turn(deck,pos,house_hand)

    
def split_hit(deck:list,pos:int,player_hand:list,house_hand:list)->tuple[int,list,int,list,list]:
    choice = ""
    while (get_score(player_hand)<=21) and (choice != "stay"):
        deck, pos, player_hand = pick(deck,pos,player_hand)

        if get_score(player_hand)>21:
                print("LOSS\nPlayer Bust\n")
                print(f"House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player Hand 1: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
                return End.lose,deck,pos, player_hand, house_hand
        
        print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
        choice = input("what do you want to do ? (hit/stay)").lower()
    return End.proceed,deck,pos,player_hand,house_hand

def split_decision():
    choice = input("what do you want to do ? (hit/stay)\n").lower()
    if choice == "hit":
        return choice
    elif choice =="stay":
        return choice
    return split_decision()

def split_player_turn(deck,pos,player_hand_1,player_hand_2,house_hand):
    choice = split_decision()

    if choice == "hit": # hit
        end1,deck,pos,player_hand_1,house_hand = split_hit(deck,pos,player_hand_1,house_hand)

        print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player hand 2: {[card.full_name for card in player_hand_2]} ({get_score(player_hand_2)})\n")
        choice = split_decision()

        if choice == "hit": # hit hit
            end2,deck,pos,player_hand_2,house_hand = split_hit(deck,pos,player_hand_2,house_hand)
            return end1,end2,deck,pos,player_hand_1,player_hand_2
        else: # hit stay
            return end1,End.proceed,deck,pos,player_hand_1,player_hand_2
        
    elif choice == "stay": # stay 
        print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player hand 2: {[card.full_name for card in player_hand_2]} ({get_score(player_hand_2)})\n")
        choice = split_decision()
        if choice == "hit": # stay hit
            end2,deck,pos,player_hand_2,house_hand = split_hit(deck,pos,player_hand_2,house_hand)
            return End.proceed,end2,deck,pos,player_hand_1,player_hand_2
        else: #stay stay
            return End.proceed,End.proceed,deck,pos,player_hand_1,player_hand_2
    
def split_evaluate_phase(end:list,deck:list,pos:int,player_hand_1:list,player_hand_2:list,house_hand:list)->tuple[list,list,int,list,list]:
    """returns [end1,end2], [deck], pos, [player_hand_1,player_hand_2],[house_hand,house_hand]"""
    if End.proceed not in end: # cas où le joueur a bust ses deux mains
        return end,deck,pos,[player_hand_1,player_hand_2],[house_hand,house_hand]
    scores = []
    
    # hand 1
    print(f"House: \n{[card.full_name for card in house_hand]} ({get_score(house_hand)}) \n\n Player hand 1: {[card.full_name for card in player_hand_1]} ({get_score(player_hand_1)})\n")
    if get_score(player_hand_1)>21:
        scores+=[End.lose]
    
    elif get_score(house_hand)< get_score(player_hand_1) or get_score(house_hand)> 21:
        print("CONGRATS ! You win !\n")
        scores += [End.win]
            
    elif get_score(house_hand) == get_score(player_hand_1) and get_score(house_hand) < 21:
        print("DRAW ! Better luck next time ! \n")
        scores += [End.draw] 
    
    elif get_score(house_hand) > get_score(player_hand_1) and get_score(house_hand) < 21:
        print("YOU LOST\n")
        scores += [End.lose]
    
    # hand 2
    print(f"House: \n{[card.full_name for card in house_hand]} ({get_score(house_hand)}) \n\n Player hand 2: {[card.full_name for card in player_hand_2]} ({get_score(player_hand_2)})\n")
    if get_score(player_hand_2)>21:
        scores+=[End.lose]
    
    elif get_score(house_hand)< get_score(player_hand_2) or get_score(house_hand)> 21:
        print("CONGRATS ! You win !\n")
        scores += [End.win]
            
    elif get_score(house_hand) == get_score(player_hand_2) and get_score(house_hand) < 21:
        print("DRAW ! Better luck next time ! \n")
        scores += [End.draw] 
    
    elif get_score(house_hand) > get_score(player_hand_2) and get_score(house_hand) < 21:
        print("YOU LOST\n")
        scores += [End.lose]

    return scores,deck,pos,[player_hand_1,player_hand_2],[house_hand,house_hand]
    
    

def split(deck,pos,player_hand,house_hand):
    """la fonction la plus dégueu jamais créée"""

    deck,pos,player_hand_1,player_hand_2 = split_cards(deck,pos,player_hand)
    print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player hand 1: {[card.full_name for card in player_hand_1]} ({get_score(player_hand_1)})\n")
    
    end1,end2,deck,pos,player_hand_1,player_hand_2= split_player_turn(deck,pos,player_hand_1,player_hand_2,house_hand)
    deck,pos,house_hand= split_house_turn(deck,pos,house_hand)
    end,deck,pos,player_hands,house_hands = split_evaluate_phase([end1,end2],deck,pos,player_hand_1,player_hand_2,house_hand)

    return end,deck,pos,player_hands,house_hands
    
