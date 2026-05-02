class Suit:
    spades = "spades ♠️ "
    hearts = "hearts ♥️ "
    clubs = "clubs ♣️ "
    diamonds = "diamonds ♦️ "


class GameResult:
    WIN = 1
    LOSE = 0
    DRAW = -1
    PROCEED = -2


class Payout:
    """This class is for the compute_gain func because I can't use GameResult 
    for the payout. Takes into account simple win, double, blackjack, draw and loss scenario

    Note: Blackjack outcome is rounded as I use integers and not float
    """
    WIN = 1.0        # player gains bet × 1
    BLACKJACK = 1.5  # player gains bet × 1.5  
    DOUBLE = 2.0     # player gains bet × 2
    DRAW = 0.0       # break even — bet returned, no gain/loss
    LOSE = -1.0      # player loses the bet


class Bet:
    OPTIONS = [5, 10, 15, 50]
    PROMPT = "How much do you want to bet? (5 / 10 / 15 / 50) 🪙 : "


class Wallet:
    STARTING_CAPITAL = 100


class Rules:
    """The dealer must hit on 16 and stand on 17.
    
    Also I'm using a classic deck, not like the casino using multiple decks. 
    Meaning, you can count cards if you want idc. 
    """
    BLACKJACK = 21
    DEALER_STAND = 17
    DECK_SIZE = 52
    START_CARDS = 4
