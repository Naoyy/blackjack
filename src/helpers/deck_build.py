from config import Suit

RANK_NAMES = ["None", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = [Suit.spades, Suit.hearts, Suit.clubs, Suit.diamonds]


class Card:
    def __init__(self, rank: int, suit: str) -> None:
        self.value = rank if rank < 11 else 10
        self.name = RANK_NAMES[rank]
        self.suit = suit
        self.full_name = f"{RANK_NAMES[rank]} of {suit}"

    def __repr__(self) -> str:
        return self.full_name


non_shuffled_deck = [Card(rank, suit) for rank in range(1, 14) for suit in SUITS]
