import uuid
import pandas as pd
from pathlib import Path
from random import shuffle

from helpers.game_builder import Turn
from helpers.deck_build import non_shuffled_deck
from config import GameResult, Payout, Bet, Wallet

DATA_DIR = Path("data")
CACHE_FILE = DATA_DIR / "cache.csv"


# ---------------------------------------------------------------------------
# Payout
# ---------------------------------------------------------------------------

def compute_gain(result: int, bet: int, is_blackjack: bool = False, is_double: bool = False) -> int:
    """Convert a GameResult into a net coin (can be negative).

    Like I said GameResult can't be used as
    multipliers for payout so we'll use this func and the Payout class to get your gains:
      WIN   -> +bet (normal) | +1.5xbet (blackjack) | +2xbet (double)
      DRAW  ->  0   (even)
      LOSE  -> -bet (normal) | -2xbet (double)
    """
    if result == GameResult.WIN:
        if is_blackjack:
            return int(bet * Payout.BLACKJACK)
        if is_double:
            return int(bet * Payout.DOUBLE)
        return bet
    if result == GameResult.DRAW:
        return 0
    # LOSE
    return -int(bet * Payout.DOUBLE) if is_double else -bet


# ---------------------------------------------------------------------------
# Betting
# ---------------------------------------------------------------------------

def ask_bet(capital: int) -> int:
    """Prompt until the player picks a valid bet they can afford."""
    affordable = [b for b in Bet.OPTIONS if b <= capital]

    options_str = " / ".join(str(b) for b in affordable)
    prompt = f"How much do you want to bet? ({options_str}) 🪙 : "

    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and int(raw) in affordable:
            return int(raw)
        print(f"  Please pick one of: {options_str}")


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def get_menu_choice() -> str:
    """Game Menu,

    Start game: starts a new game with new capital if it's your first game or your previous one if not

    Check Rules: just redirect to Blackjack rules

    Quit: if you want to leave game    
    """
    has_stats = CACHE_FILE.is_file()
    options = ["start game", "check rules", "quit"]
    if has_stats:
        options.insert(1, "check stats")

    prompt = "Welcome! What do you want to do? (" + " / ".join(o.title() for o in options) + "): "

    while True:
        choice = input(prompt).strip().lower()
        if choice in options:
            return choice


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def show_stats() -> None:
    """Show stats option: win rate, total gain, balance and last 5 rounds

    You start with 100 so if your total gain + 100 differ from your balance 
    it just means you cheated in the game files xD
    """
    if not CACHE_FILE.is_file():
        print("No stats yet — play at least one game first!\n")
        return

    df = pd.read_csv(CACHE_FILE, index_col=0)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)
    
    # Exclude DRAW (-1) from win rate — only count decisive outcomes
    finished = df[df["end"].isin([GameResult.WIN, GameResult.LOSE])]
    win_rate = finished["end"].mean() if not finished.empty else 0.0

    total_gain = df["gain"].sum()
    print(f"\n🪙  Win rate      : {win_rate:.1%} ({df['game_id'].nunique()} Games)")
    print(f"📈  Total gain    : {'+' if total_gain >= 0 else ''}{total_gain} 🪙")
    print(f"📊  Last 5 rounds :\n{df.tail()}\n")

def get_last_capital() -> int:
    """Return last known capital from cache, or starting capital if none."""
    if not CACHE_FILE.is_file():
        return Wallet.STARTING_CAPITAL

    df = pd.read_csv(CACHE_FILE)
    if df.empty or "capital_after" not in df.columns:
        return Wallet.STARTING_CAPITAL

    return int(df["capital_after"].iloc[-1])

# ---------------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------------

def save_results(results: dict) -> None:
    """Save results into a CSV"""
    new_df = pd.DataFrame(results)

    if CACHE_FILE.is_file():
        existing = pd.read_csv(CACHE_FILE, index_col=0)
        new_df = pd.concat([existing, new_df], ignore_index=True)

    new_df.to_csv(CACHE_FILE)


# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------

def play_game() -> None:
    deck = non_shuffled_deck.copy()
    shuffle(deck)
    pos = 0
    capital = get_last_capital()

    print("\n=== BLACKJACK 🃏 ===\n")
    if CACHE_FILE.is_file():
        print(f"🔄 Resuming the game with saved capital : {capital} 🪙\n")
        if capital == 0:
            print(f"💸 You're broke dude… 🥀 alright, I’ll let you play just this once 🎁\n💰 100 coins have been added to your capital.")
            capital = Wallet.STARTING_CAPITAL
    else:
        print(f"🆕 New game: starting capital {capital} 🪙\n")

    results: dict[str, list] = {
        "game_id": [],
        "end": [],
        "bet": [],
        "gain": [],
        "capital_after": [],
        "player_hand": [],
        "house_hand": [],
    }

    while capital > 0:
        print(f"💰 Capital : {capital} 🪙")
        bet = ask_bet(capital)

        game_id = str(uuid.uuid4())[:8]  # short unique ID in case we split

        result, deck, pos, player_hand, house_hand, action = Turn.house(
            *Turn.player(
                *Turn.start(deck, pos)
            )
        )

        # Normalise: split returns lists, normal play returns scalars
        is_split = isinstance(result, list)
        ends    = result      if is_split else [result]
        p_hands = player_hand if is_split else [player_hand]
        h_hands = house_hand  if is_split else [house_hand]

        # Each hand in a split plays for the full original bet.
        # No upfront deduction — compute_gain() returns a net delta:
        #   WIN  → +bet  |  DRAW → 0  |  LOSE → -bet
        hand_bets = [bet] * len(ends)

        round_gain = 0
        for end, p, h, hand_bet in zip(ends, p_hands, h_hands, hand_bets):
            gain = compute_gain(end, hand_bet, is_blackjack=(action == "blackjack"), is_double=(action == "double"))
            capital = max(capital + gain, 0)  # floor at 0
            round_gain += gain

            results["game_id"].append(game_id)
            results["end"].append(end)
            results["bet"].append(hand_bet)
            results["gain"].append(gain)
            results["capital_after"].append(capital)
            results["player_hand"].append([card.full_name for card in p])
            results["house_hand"].append([card.full_name for card in h])

        print(f"  → {'+' if round_gain >= 0 else ''}{round_gain} 🪙  |  Capital : {capital} 🪙\n")

        if capital <= 0:
            print("💸 You're out of coins — game over!\n")
            break

        again = input("Play again? (yes / quit): ").strip().lower()
        if again != "yes":
            break

    save_results(results)
    print(f"Results saved. Final capital: {capital} 🪙\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    while True:
        choice = get_menu_choice()

        if choice == "quit":
            print("Goodbye!")
            break

        if choice == "check rules":
            print("\nRules: https://bicyclecards.com/how-to-play/blackjack\n")

        if choice == "check stats":
            show_stats()

        if choice == "start game":
            play_game()


if __name__ == "__main__":
    main()
