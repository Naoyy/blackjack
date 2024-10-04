from config import End,Color
from utils.turn import *
from helpers.deck_build import Card
from operator import itemgetter 

class Turn:
    @staticmethod
    def start(deck:list,pos:int)->tuple[int,list,int,list|None,list|None]: 
        """deck for starting card, pos for position before reshuffle
    returns:
     - the end (win/lose/draw/proceed)
     - card deck for the next step (either player turn or re start) 
     - position
     - player hand/None
     - house hand/none"""
        cards,deck,pos = get_cards(deck=deck,pos=pos,start=True)
        ind_p = [0,2]
        ind_h = [1,3]
        player_hand= itemgetter(*ind_p)(cards)
        house_hand = itemgetter(*ind_h)(cards)  

        print("GAME START\n")

        if get_score(player_hand) == get_score(house_hand)== 21:
            print(f"DRAW \n\n House: \n\n {[card.full_name for card in house_hand]} (BlackJack) \n\n Player hand: {[card.full_name for card in player_hand]} (BlackJack)\n")
            return  End.draw, deck,pos, player_hand,house_hand
        elif get_score(house_hand)== 21:
            print(f"LOSS \n\n House: \n\n {[card.full_name for card in house_hand]} (BlackJack) \n\n Player hand: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
            return  End.lose, deck,pos, player_hand,house_hand
        elif get_score(player_hand)==21:
            print(f"WIN \n\n House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player hand: {[card.full_name for card in player_hand]} (BlackJack)\n")
            return  End.win, deck,pos, player_hand,house_hand
        
        return End.proceed, deck,pos, player_hand,house_hand

    @staticmethod 
    def player(end:int,deck:list,pos:int,player_hand:list=None,house_hand:list=None)->tuple[int,list,int,list,list]:   
        if end != End.proceed:
            return end, deck, pos ,player_hand, house_hand

        print(f"Player turn \n\n House: \n\n {house_hand[0].full_name} + Hidden Card \n\n Player hand: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
        choice = player_decision(player_hand)
        args = [deck,pos,player_hand,house_hand]

        if choice == "hit":
            return hit(*args)
        
        if choice == "double":
            return double(*args)
        
        if choice == "split": #TODO IMPLEMENTER CAR C LA MERD
            print("NOT YET IMPLEMENTED")
            return Turn.player(end,*args)
            # deck,pos, player_hand_1,player_hand_2 = split(deck,pos,player_hand) 
            # end1,deck,pos,player_hand_1, house_hand = Turn.player(end,deck,pos,player_hand_1,house_hand)
            # end2,deck,pos,player_hand_2, house_hand = Turn.player(end,deck, pos, player_hand_2,house_hand)

            # return [end1,end2],deck, pos, [player_hand_1,player_hand_2],[house_hand,house_hand]
        
        if choice == "stay":
            return end,*args
        
        return Turn.player(end,*args)
    
    @staticmethod
    def house(end:int,deck:list,pos:int,player_hand:list=None,house_hand:list=None)->tuple[int,list,int,list,list]:
        if end != End.proceed:
            return end,deck,pos,player_hand,house_hand
        
        if get_score(house_hand)>16 and get_score(house_hand)<21:
            print(f"House: \n{[card.full_name for card in house_hand]} ({get_score(house_hand)}) \n\n Player hand: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
            if get_score(house_hand)< get_score(player_hand):
                print("CONGRATS ! You win !\n")
                return End.win,deck,pos,player_hand,house_hand
            
            elif get_score(house_hand) == get_score(player_hand):
                print("DRAW ! Better luck next time ! \n")
                return End.draw ,deck,pos,player_hand,house_hand
            
            elif get_score(house_hand) > get_score(player_hand):
                print("YOU LOST\n")
                return End.lose, deck, pos,player_hand,house_hand

        deck,pos,house_hand= pick(deck, pos, house_hand)
        
        if get_score(house_hand)>21:
            print(f"House: \n{[card.full_name for card in house_hand]} ({get_score(house_hand)}) \n\n Player hand: {[card.full_name for card in player_hand]} ({get_score(player_hand)})\n")
            print("CONGRATS ! You win, house bust\n")
            return End.win,deck,pos,player_hand,house_hand
        
        return Turn.house(end,deck,pos,player_hand,house_hand)