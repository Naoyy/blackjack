from random import shuffle
from config import GameResult, Rules


# ---------------------------------------------------------------------------
# Deck utilities (manage deck)
# ---------------------------------------------------------------------------

def draw_cards(deck: list, pos: int, count: int = 1) -> tuple[list, list, int]:
    """Draw `count` cards from the deck at `pos`. Reshuffles if deck ends.

    Returns:
        drawn_cards, deck, new_pos
    """
    end = pos + count
    if end > Rules.DECK_SIZE:
        drawn = deck[pos:]
        shuffle(deck)
        drawn += deck[: end % Rules.DECK_SIZE]
        return drawn, deck, end % Rules.DECK_SIZE
    return deck[pos:end], deck, end


# ---------------------------------------------------------------------------
# Score calculation
# ---------------------------------------------------------------------------

def get_values(hand: list) -> list[int]:
    """Calculate values of a hand
    Returns:
        list
    """
    return [card.value for card in hand]


def get_score(hand: list) -> int:
    """Returns the best Blackjack score for `hand` (aces count as 1 or 11)."""
    values = sorted(get_values(hand))
    total = sum(v for v in values if v != 1)

    for _ in range(values.count(1)):
        total += 11 if total + 11 <= Rules.BLACKJACK else 1

    return total


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def hand_str(hand: list) -> str:
    return str([card.full_name for card in hand])


def show_table(player_hand: list, house_hand: list, hide_house: bool = True) -> None:
    """Displays the house and the player's hand with house's hand hidden if needed
    
    """
    house_display = f"{house_hand[0].full_name} + Hidden" if hide_house else hand_str(house_hand)
    print(f"\nHouse  : {house_display}")
    print(f"Player : {hand_str(player_hand)} ({get_score(player_hand)})\n")


# ---------------------------------------------------------------------------
# Player decisions
# ---------------------------------------------------------------------------

def ask_player(options: list[str]) -> str:
    """Prompt the player until a valid choice is made."""
    prompt = f"Your move ({'/'.join(options)}): "
    while True:
        choice = input(prompt).strip().lower()
        if choice in options:
            return choice


def get_player_action(player_hand: list) -> str:
    """Return available actions depending on hand state."""
    if len(player_hand) > 2:
        return ask_player(["hit", "stay"])
    if player_hand[0].value == player_hand[1].value:
        return ask_player(["double", "split", "hit", "stay"])
    return ask_player(["double", "hit", "stay"])


# ---------------------------------------------------------------------------
# Core actions
# ---------------------------------------------------------------------------

def pick(deck: list, pos: int, hand: list) -> tuple[list, int, list]:
    """Draw one card and add it to `hand`. Returns deck, pos, hand."""
    drawn, deck, pos = draw_cards(deck, pos, count=1)
    return deck, pos, list(hand) + [drawn[0]]


def hit(deck: list, pos: int, player_hand: list, house_hand: list) -> tuple:
    """Player hits repeatedly until bust or stay."""
    while get_score(player_hand) < Rules.BLACKJACK:
        deck, pos, player_hand = pick(deck, pos, player_hand)
        score = get_score(player_hand)

        if score > Rules.BLACKJACK:
            print("BUST — you lose.")
            show_table(player_hand, house_hand, hide_house=False)
            return GameResult.LOSE, deck, pos, player_hand, house_hand

        show_table(player_hand, house_hand)
        if ask_player(["hit", "stay"]) == "stay":
            break

    return GameResult.PROCEED, deck, pos, player_hand, house_hand


def double(deck: list, pos: int, player_hand: list, house_hand: list) -> tuple:
    """Player double: draw exactly one card, then stay."""
    deck, pos, player_hand = pick(deck, pos, player_hand)
    show_table(player_hand, house_hand)

    if get_score(player_hand) > Rules.BLACKJACK:
        print("BUST — you lose.")
        return GameResult.LOSE, deck, pos, player_hand, house_hand

    return GameResult.PROCEED, deck, pos, player_hand, house_hand


# ---------------------------------------------------------------------------
# Evaluate a single hand against the house
# ---------------------------------------------------------------------------

def evaluate_hand(player_hand: list, house_hand: list) -> int:
    """Compare a player hand to the house hand and return a GameResult."""
    player_score = get_score(player_hand)
    house_score = get_score(house_hand)

    print(f"\nHouse : {hand_str(house_hand)} ({house_score})")
    print(f"Player: {hand_str(player_hand)} ({player_score})\n")

    if player_score > Rules.BLACKJACK:
        print("Bust — you lose.")
        return GameResult.LOSE
    if house_score > Rules.BLACKJACK or player_score > house_score:
        print("You win!")
        return GameResult.WIN
    if player_score == house_score:
        print("Draw.")
        return GameResult.DRAW
    print("You lose.")
    return GameResult.LOSE


# ---------------------------------------------------------------------------
# Split logic
# ---------------------------------------------------------------------------

def split_cards(deck: list, pos: int, player_hand: list) -> tuple[list, int, list, list]:
    """Split a pair into two hands, each receiving one new card."""
    hand1 = [player_hand[0]]
    hand2 = [player_hand[1]]
    deck, pos, hand1 = pick(deck, pos, hand1)
    deck, pos, hand2 = pick(deck, pos, hand2)
    return deck, pos, hand1, hand2


def dealer_draw(deck: list, pos: int, house_hand: list) -> tuple[list, int, list]:
    """Dealer draws until reaching the stay threshold or busting."""
    while get_score(house_hand) <= Rules.DEALER_STAND:
        deck, pos, house_hand = pick(deck, pos, house_hand)
    return deck, pos, house_hand


def play_split_hand(deck: list, pos: int, hand: list, house_hand: list, label: str) -> tuple:
    """Play a single hand during a split round. Returns (result, deck, pos, hand)."""
    print(f"\n--- {label} ---")
    show_table(hand, house_hand)

    action = ask_player(["hit", "stay"])
    if action == "hit":
        result, deck, pos, hand, house_hand = hit(deck, pos, hand, house_hand)
    else:
        result = GameResult.PROCEED

    return result, deck, pos, hand


def split(deck: list, pos: int, player_hand: list, house_hand: list) -> tuple:
    """Handle a full split round: two hands played then evaluated against dealer."""
    deck, pos, hand1, hand2 = split_cards(deck, pos, player_hand)

    result1, deck, pos, hand1 = play_split_hand(deck, pos, hand1, house_hand, "Hand 1")
    result2, deck, pos, hand2 = play_split_hand(deck, pos, hand2, house_hand, "Hand 2")

    deck, pos, house_hand = dealer_draw(deck, pos, house_hand)

    end1 = result1 if result1 != GameResult.PROCEED else evaluate_hand(hand1, house_hand)
    end2 = result2 if result2 != GameResult.PROCEED else evaluate_hand(hand2, house_hand)

    return [end1, end2], deck, pos, [hand1, hand2], [house_hand, house_hand]
