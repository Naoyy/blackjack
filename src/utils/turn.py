from random import shuffle
from config import GameResult, Rules


def draw_cards(deck: list, pos: int, count: int = 1) -> tuple[list, list, int]:
    end = pos + count
    if end > Rules.DECK_SIZE:
        drawn = deck[pos:]
        shuffle(deck)
        drawn += deck[: end % Rules.DECK_SIZE]
        return drawn, deck, end % Rules.DECK_SIZE
    return deck[pos:end], deck, end


def get_score(hand: list) -> int:
    values = sorted([card.value for card in hand])
    total = sum(v for v in values if v != 1)
    for _ in range(values.count(1)):
        total += 11 if total + 11 <= Rules.BLACKJACK else 1
    return total


def hand_str(hand: list) -> str:
    return str([card.full_name for card in hand])


def pick(deck: list, pos: int, hand: list) -> tuple[list, int, list]:
    drawn, deck, pos = draw_cards(deck, pos, count=1)
    return deck, pos, list(hand) + [drawn[0]]


def dealer_draw(deck: list, pos: int, house_hand: list) -> tuple[list, int, list]:
    while get_score(house_hand) <= Rules.DEALER_STAND:
        deck, pos, house_hand = pick(deck, pos, house_hand)
    return deck, pos, house_hand


def evaluate_hand(player_hand: list, house_hand: list) -> int:
    player_score = get_score(player_hand)
    house_score = get_score(house_hand)
    if player_score > Rules.BLACKJACK:
        return GameResult.LOSE
    if house_score > Rules.BLACKJACK or player_score > house_score:
        return GameResult.WIN
    if player_score == house_score:
        return GameResult.DRAW
    return GameResult.LOSE


def split_cards(deck: list, pos: int, player_hand: list) -> tuple[list, int, list, list]:
    hand1 = [player_hand[0]]
    hand2 = [player_hand[1]]
    deck, pos, hand1 = pick(deck, pos, hand1)
    deck, pos, hand2 = pick(deck, pos, hand2)
    return deck, pos, hand1, hand2
